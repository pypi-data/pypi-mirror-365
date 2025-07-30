"""reaction_info_extractor_clean.py

Single-file, maintainable CLI tool that pulls **enzyme-reaction performance data**
from chemistry PDFs using Google Gemini (text-only *and* vision) - now with
**true figure-image extraction** mirroring the enzyme-lineage workflow.

Key June 2025 additions
=======================
1. **Figure image helper** - locates the figure caption, then exports the first
   image **above** that caption using PyMuPDF (fitz). This PNG is sent to
   Gemini Vision for metric extraction.
2. **GeminiClient.generate()** now accepts an optional `image_b64` arg and
   automatically switches to a *vision* invocation when provided.
3. **extract_metrics_for_enzyme()** chooses between three tiers:

      * *Table* -> caption + following rows (text-only)
      * *Figure* -> image bytes (vision) *or* caption fallback
      * *Other* -> page-level text

   If the vision route fails (no JSON), it gracefully falls back to caption
   text so the pipeline never crashes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import subprocess
import sys
import time
from base64 import b64encode, b64decode
from collections import OrderedDict
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from textwrap import dedent
from typing import Any, Dict, List, Optional, Tuple, Union

# Import universal caption pattern
try:
    from .caption_pattern import get_universal_caption_pattern
    from .campaign_utils import enhance_prompt_with_campaign, get_location_hints_for_campaign
except ImportError:
    # Fallback if running as standalone script
    from caption_pattern import get_universal_caption_pattern
    from campaign_utils import enhance_prompt_with_campaign, get_location_hints_for_campaign

import fitz  # PyMuPDF - for image extraction
import google.generativeai as genai  # type: ignore
import pandas as pd
from PyPDF2 import PdfReader
import io

###############################################################################
# 1 - CONFIG & CONSTANTS
###############################################################################

@dataclass
class Config:
    """Centralised tunables so tests can override them easily."""

    model_name: str = "gemini-2.5-flash"
    location_temperature: float = 0.0
    extract_temperature: float = 0.0
    model_reaction_temperature: float = 0.0
    top_p: float = 1.0
    max_tokens: int = 32000
    pdf_cache_size: int = 8
    retries: int = 2

@dataclass
class CompoundMapping:
    """Mapping between compound identifiers and IUPAC names."""
    identifiers: List[str]
    iupac_name: str
    common_names: List[str] = field(default_factory=list)
    compound_type: str = "unknown"
    source_location: Optional[str] = None

###############################################################################
# 2 - LOGGING
###############################################################################

LOGGER = logging.getLogger("reaction_info_extractor")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s [%(name)s] %(message)s"))
LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)

# === OPSIN VALIDATION === -------------------------------------------------

def is_valid_iupac_name_with_opsin(name: str) -> bool:
    """Check if a name is a valid IUPAC name using the local OPSIN command."""
    if not name or len(name.strip()) < 3:
        return False
    
    # Skip if it looks like a compound ID (e.g., "1a", "S1", etc.)
    if re.match(r'^[0-9]+[a-z]?$|^S\d+$', name.strip()):
        return False
    
    try:
        # Use local OPSIN command to check if name can be converted to SMILES
        process = subprocess.run(
            ['opsin', '-o', 'smi'],
            input=name.strip(),
            text=True,
            capture_output=True,
            timeout=30
        )
        
        # If OPSIN successfully converts to SMILES, the name is valid IUPAC
        if process.returncode == 0 and process.stdout.strip():
            output = process.stdout.strip()
            # Check if output looks like a valid SMILES (contains common SMILES characters)
            if any(char in output for char in 'CNOS()=[]#+-'):
                return True
        
        return False
            
    except Exception as e:
        LOGGER.debug(f"OPSIN check failed for '{name}': {e}")
        return False

# --- Debug dump helper ----------------------------------------------------
def _dump(text: str | bytes, path: Path | str) -> None:
    """Write `text` / `bytes` to `path`, creating parent dirs as needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    mode = "wb" if isinstance(text, (bytes, bytearray)) else "w"
    with p.open(mode) as fh:
        fh.write(text)

###############################################################################
# 3 - PDF UTILITIES
###############################################################################

def extract_text_by_page(path: Optional[Path]) -> List[str]:
    if path is None:
        return []
    reader = PdfReader(str(path))
    pages: List[str] = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("PyPDF2 failed on a page: %s", exc)
            pages.append("")
    return pages

###############################################################################
# 4 - GEMINI WRAPPER (text & vision)
###############################################################################

def get_model(cfg: Config):
    """Configure API key and return a `GenerativeModel` instance."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("Set the GEMINI_API_KEY environment variable.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(cfg.model_name)

# Bounded LRU caches to store prompt/image content by hash (prevents memory leaks)

class LRUCache:
    """Simple LRU cache implementation."""
    def __init__(self, maxsize: int):
        self.maxsize = maxsize
        self.cache = OrderedDict()
    
    def get(self, key: str) -> Optional[str]:
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def put(self, key: str, value: str) -> None:
        if key in self.cache:
            # Update existing
            self.cache.move_to_end(key)
        else:
            # Add new, evict oldest if needed
            if len(self.cache) >= self.maxsize:
                self.cache.popitem(last=False)
        self.cache[key] = value
    
    def __len__(self) -> int:
        return len(self.cache)

# Global bounded caches
_PROMPT_CACHE = LRUCache(maxsize=1000)
_IMAGE_CACHE = LRUCache(maxsize=500)  # Images are larger, so smaller cache

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics for debugging."""
    return {
        "gemini_cache_info": _cached_gemini_call.cache_info(),
        "prompt_cache_size": len(_PROMPT_CACHE),
        "image_cache_size": len(_IMAGE_CACHE),
    }

@lru_cache(maxsize=1000)
def _cached_gemini_call(
    model_name: str,
    prompt_hash: str,
    image_hash: Optional[str],
    temperature: float,
    max_retries: int,
) -> str:
    """Pure cached function for Gemini API calls using only hash keys.
    
    Args:
        model_name: Name of the Gemini model
        prompt_hash: SHA256 hash of the prompt
        image_hash: SHA256 hash of the image (if any)
        temperature: Temperature for generation
        max_retries: Maximum number of retries
    
    Returns:
        Raw response text from Gemini
    """
    # Retrieve actual content from LRU cache
    prompt = _PROMPT_CACHE.get(prompt_hash)
    image_b64 = _IMAGE_CACHE.get(image_hash) if image_hash else None
    
    if prompt is None:
        raise RuntimeError(f"Prompt content not found for hash {prompt_hash}")
    
    # Configure API key (this is idempotent)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("Set the GEMINI_API_KEY environment variable.")
    genai.configure(api_key=api_key)
    
    # Create model instance (not cached since it's lightweight)
    model = genai.GenerativeModel(model_name)
    
    for attempt in range(1, max_retries + 1):
        try:
            # Handle image if provided
            if image_b64:
                # Decode base64 string to bytes for Gemini API
                image_bytes = b64decode(image_b64)
                parts = [prompt, {"mime_type": "image/png", "data": image_bytes}]
            else:
                parts = [prompt]
            
            resp = model.generate_content(
                parts,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": 32000,  # Increased for better extraction
                }
            )
            # Track token usage if available
            try:
                if hasattr(resp, 'usage_metadata'):
                    input_tokens = getattr(resp.usage_metadata, 'prompt_token_count', 0)
                    output_tokens = getattr(resp.usage_metadata, 'candidates_token_count', 0)
                    if input_tokens or output_tokens:
                        try:
                            from .wrapper import add_token_usage
                            add_token_usage('reaction_info_extractor', input_tokens, output_tokens)
                        except ImportError:
                            pass  # wrapper not available
            except Exception:
                pass  # token tracking is best-effort
            
            return resp.text.strip()
        except Exception as exc:
            if attempt == max_retries:
                raise
            time.sleep(2 ** attempt)
    
    # Should never reach here
    raise RuntimeError("Max retries exceeded")

def _normalize_prompt_for_caching(prompt: str) -> str:
    """Normalize prompt for better cache hit rates by removing boilerplate and collapsing whitespace."""
    # Remove common boilerplate lines that don't affect the core query
    lines = prompt.split('\n')
    normalized_lines = []
    
    for line in lines:
        # Skip timestamp and debug lines
        if any(skip in line.lower() for skip in ['timestamp:', 'length:', 'characters', '===', '***']):
            continue
        # Skip lines that are just separators
        if line.strip() and not line.strip().replace('=', '').replace('-', '').replace('*', ''):
            continue
        # Collapse whitespace but preserve structure
        normalized_lines.append(' '.join(line.split()))
    
    # Join and collapse multiple newlines
    normalized = '\n'.join(normalized_lines)
    normalized = re.sub(r'\n\s*\n+', '\n\n', normalized)
    
    return normalized.strip()

def generate_json_with_retry(
    model,
    prompt: str,
    schema_hint: str | None = None,
    *,
    max_retries: int = 2,
    temperature: float = 0.0,
    debug_dir: str | Path | None = None,
    tag: str = 'gemini',
    image_b64: Optional[str] = None,
):
    """Call Gemini with retries & exponential back-off, returning parsed JSON."""
    # Generate cache keys based on normalized prompt and image content
    normalized_prompt = _normalize_prompt_for_caching(prompt)
    prompt_hash = hashlib.sha256(normalized_prompt.encode()).hexdigest()
    image_hash = hashlib.sha256(image_b64.encode()).hexdigest() if image_b64 else None
    
    # Log prompt details
    LOGGER.info("=== GEMINI API CALL: %s ===", tag.upper())
    LOGGER.info("Prompt length: %d characters", len(prompt))
    LOGGER.info("Prompt hash: %s", prompt_hash[:16])
    if image_hash:
        LOGGER.info("Image hash: %s", image_hash[:16])
    LOGGER.info("First 500 chars of prompt:\n%s\n...(truncated)", prompt[:500])
    
    # Save full prompt to debug directory if provided
    if debug_dir:
        debug_path = Path(debug_dir)
        debug_path.mkdir(parents=True, exist_ok=True)
        prompt_file = debug_path / f"{tag}_prompt_{int(time.time())}.txt"
        _dump(f"=== PROMPT FOR {tag.upper()} ===\nTimestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\nLength: {len(prompt)} characters\nHash: {prompt_hash}\n{'='*80}\n\n{prompt}",
              prompt_file)
        LOGGER.info("Full prompt saved to: %s", prompt_file)
    
    try:
        # Store content in bounded LRU caches for the cached function to retrieve
        _PROMPT_CACHE.put(prompt_hash, prompt)
        if image_hash and image_b64:
            _IMAGE_CACHE.put(image_hash, image_b64)
        
        # Check if this will be a cache hit
        cache_info_before = _cached_gemini_call.cache_info()
        
        # Use cached Gemini call (only with hash keys)
        LOGGER.info("Calling cached Gemini API...")
        raw = _cached_gemini_call(
            model_name=model.model_name,
            prompt_hash=prompt_hash,
            image_hash=image_hash,
            temperature=temperature,
            max_retries=max_retries,
        )
        
        # Log cache performance
        cache_info_after = _cached_gemini_call.cache_info()
        if cache_info_after.hits > cache_info_before.hits:
            LOGGER.info("✓ Cache HIT for prompt hash %s", prompt_hash[:16])
        else:
            LOGGER.info("✗ Cache MISS for prompt hash %s", prompt_hash[:16])
        
        # Log response
        LOGGER.info("Gemini response length: %d characters", len(raw))
        LOGGER.info("First 500 chars of response:\n%s\n...(truncated)", raw[:500])
        
        # Save full response to debug directory
        if debug_dir:
            response_file = debug_path / f"{tag}_response_{int(time.time())}.txt"
            _dump(f"=== RESPONSE FOR {tag.upper()} ===\nTimestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\nLength: {len(raw)} characters\nHash: {prompt_hash}\n{'='*80}\n\n{raw}",
                  response_file)
            LOGGER.info("Full response saved to: %s", response_file)

        # Remove common Markdown fences more carefully
        if raw.startswith("```json"):
            raw = raw[7:].strip()  # Remove ```json
        elif raw.startswith("```"):
            raw = raw[3:].strip()  # Remove ```
        
        if raw.endswith("```"):
            raw = raw[:-3].strip()  # Remove trailing ```
        
        
        # Simple JSON parsing approach
        # Try direct parsing first
        LOGGER.debug(f"Raw JSON length: {len(raw)}")
        LOGGER.debug(f"Raw JSON first 200 chars: {raw[:200]}")
        LOGGER.debug(f"Raw JSON last 200 chars: {raw[-200:]}")
        
        # Try using json-repair first
        try:
            import json_repair
            parsed = json_repair.loads(raw)
            LOGGER.info("Successfully parsed JSON using json-repair")
        except Exception as repair_error:
            LOGGER.warning(f"json-repair failed: {repair_error}")
            # Fall back to standard json.loads
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError as e:
                LOGGER.error(f"JSON parsing failed at position {e.pos}: {e}")
                LOGGER.error(f"Character at error: {repr(raw[e.pos] if e.pos < len(raw) else 'END')}")
                LOGGER.error(f"Context: {repr(raw[max(0, e.pos-20):e.pos+20])}")
                
                # Count braces and quotes for debugging
                open_braces = raw.count('{')
                close_braces = raw.count('}')
                quotes = raw.count('"')
                LOGGER.error(f"Braces: {open_braces} open, {close_braces} close. Quotes: {quotes}")
            
            # If that fails, try to extract JSON from the response using a simpler method
            try:
                # Look for JSON array or object start
                array_start = raw.find('[')
                obj_start = raw.find('{')
                
                # Determine which comes first
                if array_start != -1 and (obj_start == -1 or array_start < obj_start):
                    # Handle array
                    start_idx = array_start
                    bracket_count = 0
                    end_idx = -1
                    for i in range(start_idx, len(raw)):
                        if raw[i] == '[':
                            bracket_count += 1
                        elif raw[i] == ']':
                            bracket_count -= 1
                            if bracket_count == 0:
                                end_idx = i + 1
                                break
                    
                    if end_idx == -1:
                        raise json.JSONDecodeError("No matching closing bracket found", raw, 0)
                    
                    json_str = raw[start_idx:end_idx]
                    LOGGER.debug(f"Extracted JSON array: {json_str[:200]}...")
                    parsed = json.loads(json_str)
                elif obj_start != -1:
                    # Handle object
                    start_idx = obj_start
                    brace_count = 0
                    end_idx = -1
                    for i in range(start_idx, len(raw)):
                        if raw[i] == '{':
                            brace_count += 1
                        elif raw[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = i + 1
                                break
                    
                    if end_idx == -1:
                        raise json.JSONDecodeError("No matching closing brace found", raw, 0)
                    
                    json_str = raw[start_idx:end_idx]
                    LOGGER.debug(f"Extracted JSON object: {json_str[:200]}...")
                    parsed = json.loads(json_str)
                else:
                    raise json.JSONDecodeError("No JSON structure found", raw, 0)
                
            except json.JSONDecodeError:
                # Final fallback - try to use eval as a last resort (unsafe but functional)
                try:
                    # Replace problematic characters and try to parse as Python structure
                    safe_raw = raw.replace('null', 'None').replace('true', 'True').replace('false', 'False')
                    
                    # Check for array or object
                    array_start = safe_raw.find('[')
                    obj_start = safe_raw.find('{')
                    
                    if array_start != -1 and (obj_start == -1 or array_start < obj_start):
                        # Handle array
                        start_idx = array_start
                        bracket_count = 0
                        end_idx = -1
                        for i in range(start_idx, len(safe_raw)):
                            if safe_raw[i] == '[':
                                bracket_count += 1
                            elif safe_raw[i] == ']':
                                bracket_count -= 1
                                if bracket_count == 0:
                                    end_idx = i + 1
                                    break
                        
                        if end_idx == -1:
                            raise ValueError("No matching closing bracket found")
                        
                        struct_str = safe_raw[start_idx:end_idx]
                    elif obj_start != -1:
                        # Handle object
                        start_idx = obj_start
                        brace_count = 0
                        end_idx = -1
                        for i in range(start_idx, len(safe_raw)):
                            if safe_raw[i] == '{':
                                brace_count += 1
                            elif safe_raw[i] == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    end_idx = i + 1
                                    break
                        
                        if end_idx == -1:
                            raise ValueError("No matching closing brace found")
                        
                        struct_str = safe_raw[start_idx:end_idx]
                    else:
                        raise ValueError("No dict or list found")
                    
                    parsed = eval(struct_str)  # This is unsafe but we trust our own generated content
                    LOGGER.warning("Used eval() fallback for JSON parsing")
                    
                except Exception:
                    # If all else fails, return empty dict
                    LOGGER.error("All JSON parsing methods failed")
                    if '[]' in raw:
                        parsed = []
                    else:
                        raise json.JSONDecodeError("No JSON structure found in response", raw, 0)
        
        LOGGER.info("Successfully parsed JSON response")
        return parsed
    except Exception as exc:
        LOGGER.error("Cached Gemini call failed: %s", exc)
        raise


###############################################################################
# 5 - PROMPTS (unchanged except for brevity)
###############################################################################

PROMPT_FIND_LOCATIONS = dedent("""
You are an expert reader of protein engineering manuscripts.
Given the following article captions and section titles, identify most promising locations
(tables or figures) that contain reaction performance data (yield, TON, TTN, ee, 
activity, etc.) for enzyme variants. 

CRITICAL PRIORITY: FULL EVOLUTION LINEAGE DATA IS REQUIRED
- Look for locations showing data for ALL enzyme variants in the evolution lineage
- Prioritize sources that show the complete evolutionary progression (parent → child variants)
- Look for captions mentioning "sequentially evolved", "evolution lineage", "rounds of evolution", "directed evolution progression"
- Sources showing data for individual variants only (e.g., just the final variant) are LESS VALUABLE than complete lineage data

IMPORTANT: Some papers have multiple enzyme lineages/campaigns with different 
performance data locations. Pay careful attention to:
- The caption text to identify which campaign/lineage the data is for
- Enzyme name prefixes that indicate different campaigns
- Different substrate/product types mentioned in captions

IMPORTANT FIGURE REFERENCE RULES:
- For figures, ALWAYS return the main figure number only (e.g., "Figure 2", NOT "Figure 2a" or "Figure 2(a)")
- The extraction system will handle retrieving the entire figure including all sub-panels
- For tables, return the complete reference as it appears

Respond with a JSON array where each element contains:
- "location": the identifier (e.g. "Table S1", "Figure 3", "Table 2", NOT "Figure 3a")
- "type": one of "table", "figure"
- "confidence": your confidence score (0-100)
- "caption": the exact caption text for this location
- "reason": brief explanation (including if this is for a specific lineage/campaign)
- "lineage_hint": any indication of which enzyme group this data is for (or null)
- "campaign_clues": specific text in the caption that indicates the campaign (enzyme names, substrate types, etc.)

PRIORITIZATION RULES:
- HIGHEST PRIORITY: Sources showing COMPLETE evolution lineage data (all variants in progression)
- MEDIUM PRIORITY: Sources showing data for multiple variants (but not complete lineage)
- LOWEST PRIORITY: Sources showing data for individual variants only

Tables are generally preferred over figures unless you are convinced that only the figure contains complete lineage reaction matrix information. Some tables don't have performance data, check provided context of the specific table.

IMPORTANT FOR TABLES: When evaluating a table, check if the context below the table shows performance values (TTN, yield, ee, etc.). If the table caption mentions enzymes but the table only shows mutations/sequences, look for performance data in the text immediately following the table. If context below the table shows numerical values, use the table location as it likely contains the referenced data.

Do not include too much sources, just return 2 or 3 sources.
Adjust confidence comparing all locations you will be returning, only rank figure the highest when you are absolutely certain table won't contain complete information.
When returning confidence scores, be more accurate and avoid scores that are too close together.

CRITICAL: 
- Return "location" EXACTLY as the first reference identifier appears in the actual caption text
- Copy the exact characters including all punctuation (periods, colons, pipes, etc.) up to the first space after the identifier
- Do NOT modify, standardize, or interpret the location - return it verbatim from the document
- Include "document" field to specify which PDF contains this location: "manuscript" or "supplementary"

CRITICAL OUTPUT REQUIREMENT:
Respond ONLY with valid JSON. NO markdown fences, no commentary, no explanations.
Start directly with [ and end with ]

Format:
[{"location": "", "type": "", "document": "", "confidence": 0, "caption": "", "reason": "", "lineage_hint": "", "campaign_clues": ""}]
""")

PROMPT_EXTRACT_METRICS = dedent("""
You are given either (a) the PNG image of a figure panel, or (b) the caption /
text excerpt that contains numeric reaction performance data for an enzyme.

Extract ONLY the performance metrics, NOT substrate/product names or reaction conditions.

CRITICAL: EXTRACT ALL AVAILABLE METRICS - DO NOT SKIP ANY METRIC THAT IS PROVIDED!

Return a JSON object with the following keys (use **null** only if the value is not mentioned at all):
  * "yield"              - yield as percentage with ONE decimal place precision (ALWAYS LOOK FOR THIS)
  * "ttn"               - turnover number (total turnovers) - CRITICAL METRIC, ALWAYS EXTRACT IF PRESENT
  * "ton"               - turnover number if TTN not available
  * "selectivity"       - ee or er value with unit (e.g., "98% ee", ">99:1 er") - CRITICAL FOR STEREOCHEMISTRY
  * "conversion"        - conversion percentage if different from yield
  * "tof"               - turnover frequency (turnovers per time unit) if provided
  * "activity"          - specific activity if provided (with unit)
  * "catalyst_form"     - the form of catalyst used (e.g., "whole cells", "clarified lysate", "purified protein")
  * "other_metrics"     - dictionary of any other performance metrics with their units
  * "notes"             - any performance-related notes

EXTRACTION PRIORITIES:
1. YIELD - Most common metric, ALWAYS extract if present (isolated yield, NMR yield, GC yield, HPLC yield, etc.)
2. TTN/TON - Critical for biocatalysis efficiency, NEVER miss this if it's mentioned anywhere
3. SELECTIVITY (ee/er/dr) - Essential for stereochemistry, extract all forms
4. ANY other numeric performance data mentioned

IMPORTANT: 
- Extract ALL performance metrics provided, even if they use different units
- Report numeric yield values ONLY (e.g., 92.3 not "92.3% yield")
- Report TTN as a number (e.g., 1500 not "1500 TTN" or "1500 turnovers")
- Look for metrics in: main text, tables, figures, captions, supplementary notes
- If you find conflicting values, use the most complete source (typically the primary figure/table)

CRITICAL: DO NOT CONFUSE DIFFERENT METRICS:
- Yield (%) measures how much product was formed (0-100%)
- Selectivity/ee (%) measures enantiomeric excess - the stereoselectivity of the reaction
- TTN (number) measures total turnovers - how many substrate molecules each enzyme converts
- These are COMPLETELY DIFFERENT values - a reaction might have 95% yield but 85% ee and 1000 TTN

CRITICAL OUTPUT REQUIREMENT:
Respond ONLY with valid JSON. NO markdown fences, no commentary, no explanations.
Start directly with { and end with }
Example: {"yield": 95.5, "ttn": 2500, "selectivity": "99% ee", "conversion": null, ...}
""")

PROMPT_EXTRACT_FIGURE_METRICS_BATCH = dedent("""
STEP 1: First, identify ALL X-axis labels in the figure
- Read each X-axis label from left to right
- List exactly what text appears under each bar/data point
- Note: Labels may be abbreviated or use different naming conventions

STEP 2: Match X-axis labels to target enzyme variants
- Compare each X-axis label against the target enzyme list below
- Look for partial matches, abbreviations, or similar naming patterns
- If an X-axis label doesn't match any target enzyme, still include it for completeness

STEP 3: Identify Y-axis scales and what they measure
- Look at the Y-axis labels and tick marks to understand what each axis measures
- If there are multiple Y-axes (left and right), read the axis labels and units
- Note the minimum and maximum values on each axis scale
- Identify which visual elements (bars, dots, lines) correspond to which axis

STEP 4: Extract values for each matched variant
- For each X-axis position, identify which visual elements belong to that position
- LEFT Y-axis (bars): Measure bar height against the left scale by reading tick marks
- RIGHT Y-axis (dots): Measure dot position against the right scale by reading tick marks
- CRITICAL: Read actual scale values from the axis labels and tick marks
- Verify: taller bars should have higher values, higher dots should have higher values

CRITICAL DATA ACCURACY REQUIREMENTS:
- DO NOT CONFUSE yield with selectivity (ee) with TTN values - these are completely different metrics
- Yield is typically shown as percentage (0-100%)
- Selectivity/ee is enantiomeric excess, also shown as percentage but measures stereoselectivity
- TTN (Total Turnover Number) is the number of substrate molecules converted per enzyme molecule
- Each enzyme variant should have its OWN yield, ee, and TTN values - do not mix values between variants
- Carefully match each bar/dot to its corresponding enzyme label on the X-axis
- If looking at grouped bars, ensure you're reading the correct bar for each metric
- Double-check that variant A's yield is not confused with variant B's yield
- If values are unclear or ambiguous, return null rather than guessing

Target enzymes to find and extract:
{enzyme_names}

CRITICAL INSTRUCTIONS FOR HANDLING MULTIPLE CONDITIONS:
- If the same enzyme is tested under multiple conditions, return ALL conditions as separate entries
- Use the EXACT enzyme name from the target list as the key (exactly as provided above)
- ALWAYS populate the "catalyst_form" field with the specific condition/form used in that experiment
- Each enzyme+condition combination should be a separate entry in your output

CRITICAL: USE PROVIDED ENZYME NAMES AS JSON KEYS:
- You MUST use the enzyme names from the "Target enzymes" list above as the JSON keys
- DO NOT use the x_axis_label as the key - that goes in the "x_axis_label" field
- For example, if target list has "C10-WIRF_GAK" and x-axis shows "+ E70K (WIRF_GAK)", use "C10-WIRF_GAK" as the key

Instructions:
1. First, list ALL X-axis labels you can see in the figure
2. Match each X-axis label to the target enzyme variants
3. For matched variants, extract both bar heights (left Y-axis) and dot positions (right Y-axis)
4. Return data only for variants that have clear X-axis labels and are matched to targets
5. If multiple conditions exist for the same enzyme, return each as a separate entry
6. Include all entries in your output, even if they have the same enzyme name

Return JSON with the identified enzyme variant names as keys containing:
  * "x_axis_label" - the exact text from the X-axis for this variant
  * "yield" - percentage from left Y-axis bar height measurement
  * "ttn" - turnover number from right Y-axis dot position measurement
  * "ton" - if TTN not available
  * "selectivity" - if shown
  * "conversion" - if different from yield
  * "catalyst_form" - the form of catalyst used (e.g., "whole cells", "clarified lysate", "purified protein", "cell-free extract")
  * "tof" - if provided
  * "activity" - if provided
  * "other_metrics" - other metrics
  * "notes" - REQUIRED: Describe the X-axis label, bar position, and dot position (e.g., "X-axis shows P411-CIS, leftmost bar is very short, dot is at bottom")

CRITICAL: Return ONLY valid JSON in this exact format:
{{"enzyme_name": {{"x_axis_label": "label", "yield": number, "ttn": number, "notes": "description"}}}}

Rules:
- Use double quotes for all strings
- No markdown, no commentary, no explanations
- All values must be properly formatted
- Ensure JSON is complete and valid
- Do not truncate or cut off the response
- IMPORTANT: When extracting data, prioritize the most complete source that shows data for ALL variants. If there are conflicting values between different sources (e.g., bar graph vs text values), use the source that provides complete data for all target enzymes and ignore partial or conflicting values from other sources
""")

# Removed substrate scope IUPAC extraction - now handled in model reaction only

PROMPT_FIND_MODEL_REACTION_LOCATION = dedent("""
You are an expert reader of chemistry manuscripts.
Given the following text sections, identify where the MODEL REACTION information is located.

The model reaction is the STANDARD reaction used to evaluate all enzyme variants 
(not the substrate scope). Look for:

- SPECIFIC compound numbers (e.g., "1a", "2a", "3a") used in the model reaction
- Reaction SCHEMES or FIGURES showing the model reaction with numbered compounds
- Tables showing reaction conditions with specific compound IDs
- Sections titled "Model Reaction", "Standard Reaction", "General Procedure" WITH compound numbers

CRITICAL REQUIREMENTS:
1. The location MUST reference SPECIFIC numbered compounds (not generic descriptions)
2. DO NOT use generic locations like "main text" or "introduction"
3. MUST be a Figure, Scheme, Table, or specific SI section
4. Look for actual compound IDs like "1a + 2a → 3a" or "substrate 1a"

Also identify where the IUPAC names for these specific compounds are listed.

Respond with a JSON object containing:
{
  "model_reaction_location": {
    "location": "SPECIFIC Figure/Scheme/Table number (e.g., 'Figure 2a', 'Scheme 1', 'Table S1')",
    "document": "manuscript" or "supplementary" - indicate which document contains this location,
    "confidence": 0-100,
    "reason": "why this contains the model reaction WITH specific compound IDs",
    "compound_ids": ["list", "of", "SPECIFIC", "compound", "IDs", "found", "e.g.", "1a", "2a", "3a"]
  },
  "conditions_location": {
    "location": "SPECIFIC location where reaction conditions are described",
    "document": "manuscript" or "supplementary" - indicate which document contains this location,
    "confidence": 0-100
  },
  "iupac_location": {
    "location": "where IUPAC names are listed (usually SI compound characterization)",
    "document": "manuscript" or "supplementary" - indicate which document contains this location,
    "confidence": 0-100,
    "compound_section_hint": "specific section to look for compound IDs"
  }
}

IMPORTANT: 
- If no SPECIFIC compound IDs are found, set compound_ids to []
- The model_reaction_location MUST be a Figure, Scheme, Table, or SI section, NOT "main text"
- Look for numbered compounds like "1a", "2a", not generic terms like "enol acetates"

CRITICAL OUTPUT REQUIREMENT:
Respond ONLY with valid JSON. NO markdown fences, no commentary, no explanations.
Start directly with { and end with }
""")

PROMPT_MODEL_REACTION = dedent("""
Extract the model/standard reaction used to evaluate enzyme variants in this paper.

This is the reaction used for directed evolution screening, NOT the substrate scope.
Look for terms like "model reaction", "standard substrate", "benchmark reaction", 
or the specific reaction mentioned in enzyme screening/evolution sections.

CRITICAL STEPS FOR COMPOUND IDENTIFICATION:
1. ALWAYS look for specific compound IDs/numbers in the model reaction (e.g., "1a", "2a", "3a", "6a", "7a")
2. If the text mentions generic terms like "enol acetates" or "silyl enol ethers", search for the SPECIFIC numbered compounds used
3. Look in reaction schemes, figures, and experimental sections for numbered compounds
4. Common patterns:
   - "compound 1a" or "substrate 1a"
   - Numbers in bold or italics (1a, 2a, etc.)
   - References like "using 1a as substrate"

CRITICAL STEPS FOR IUPAC NAMES:
1. After finding compound IDs, search the context for these IDs to find their IUPAC names
2. Look for sections with "Compound 1a:", "Product 3a:", or similar patterns
3. The IUPAC names are usually given after the compound ID in parentheses or after a colon
4. If no IUPAC name is found for a compound ID, still include the ID in substrate_list/product_list

CRITICAL FOR SUBSTRATE CONCENTRATION:
- Look carefully in FIGURES and figure captions for substrate concentration information
- Figures often show detailed reaction conditions that may not be in the main text
- Identify the ACTUAL SUBSTRATES being transformed (not reducing agents or cofactors)
- Common pattern: "[X] mM [substrate name]" or "[substrate]: [X] mM"
- DO NOT confuse reducing agents (dithionite, NADH, etc.) with actual substrates
- The substrate is the molecule being chemically transformed by the enzyme

Return a JSON object with:
  * "substrate_list" - Array of substrate identifiers as used in the paper (e.g., ["1a", "2a"]) - REQUIRED, CANNOT BE EMPTY
  * "substrate_iupac_list" - Array of IUPAC names for ALL substrates/reagents - REQUIRED, CANNOT CONTAIN NULL
  * "product_list" - Array of product identifiers as used in the paper (e.g., ["3a"]) - REQUIRED, CANNOT BE EMPTY
  * "product_iupac_list" - Array of IUPAC names for ALL products formed - REQUIRED, CANNOT CONTAIN NULL
  * "reaction_substrate_concentration" - Concentration of actual substrate(s) being transformed, NOT reducing agents like dithionite
  * "cofactor" - Any cofactors used (e.g., "NADH", "NADPH", "FAD", "heme", etc.) or null if none
  * "reaction_temperature" - reaction temperature (e.g., "25°C", "room temperature")
  * "reaction_ph" - reaction pH
  * "reaction_buffer" - buffer system (e.g., "50 mM potassium phosphate")
  * "reaction_other_conditions" - other important conditions (enzyme loading, reducing agents like dithionite, time, anaerobic, etc.)

⚠️ CRITICAL REQUIREMENTS - DO NOT RETURN INCOMPLETE DATA: ⚠️
- substrate_list and product_list MUST contain specific compound IDs - NEVER empty arrays
- substrate_iupac_list and product_iupac_list MUST contain IUPAC names for ALL compounds - NEVER null values
- If you cannot find BOTH the compound ID AND its IUPAC name, keep searching in ALL sections:
  * Experimental procedures
  * Compound characterization
  * Supporting information
  * Figure captions and schemes
- The arrays MUST have matching lengths: len(substrate_list) == len(substrate_iupac_list)
- DO NOT return partial data - either find complete information or search harder
- For IUPAC names, look for the SYSTEMATIC chemical names, NOT common/trivial names
- Search the provided context for systematic names - they typically:
  * Use numerical locants (e.g., "prop-2-enoate" not "acrylate")
  * Follow IUPAC nomenclature rules
  * May be found in compound characterization sections
- If you find a common name in the reaction description, search the context for its systematic equivalent
- Look for the exact systematic names as written in the compound characterization
- Do NOT include stereochemistry prefixes like (1R,2S) unless they are part of the compound name in the SI

CRITICAL OUTPUT REQUIREMENT:
Respond ONLY with valid JSON. NO markdown fences, no commentary, no explanations.
Start directly with { and end with }
Example: {"substrate_list": ["1a", "2a"], "substrate_iupac_list": ["(E)-1-phenylprop-2-en-1-yl acetate", "(Z)-1-phenylprop-2-en-1-yl acetate"], "product_list": ["3a", "3b"], "product_iupac_list": ["(S)-1-phenylprop-2-en-1-ol", "(R)-1-phenylprop-2-en-1-ol"], ...}
""")

PROMPT_ANALYZE_LINEAGE_GROUPS = dedent("""
You are analyzing enzyme performance data from a protein engineering manuscript.
Based on the performance data locations and enzyme names, determine if there are 
distinct enzyme lineage groups that were evolved for different purposes.

Look for patterns such as:
- Different tables/figures for different enzyme groups
- Enzyme naming patterns that suggest different lineages
- Different reaction types mentioned in notes or captions
- Clear separations in how variants are organized

Return a JSON object with:
{
  "has_multiple_lineages": true/false,
  "lineage_groups": [
    {
      "group_id": "unique identifier you assign",
      "data_location": "where this group's data is found",
      "enzyme_pattern": "naming pattern or list of enzymes",
      "reaction_type": "what reaction this group catalyzes",
      "evidence": "why you grouped these together"
    }
  ],
  "confidence": 0-100
}

If only one lineage exists, return has_multiple_lineages: false with a single group.

CRITICAL OUTPUT REQUIREMENT:
Respond ONLY with valid JSON. NO markdown fences, no commentary, no explanations.
Start directly with { and end with }
""")

PROMPT_FIND_LINEAGE_MODEL_REACTION = dedent("""
For the enzyme group with performance data in {location}, identify the specific 
model reaction used to screen/evaluate these variants.

Context about this group:
{group_context}

Look for:
- References to the specific substrate/product used for this enzyme group
- Text near the performance data location describing the reaction
- Connections between the enzyme names and specific substrates
- Any mention of "screened with", "tested against", "substrate X was used"

Return:
{{
  "substrate_ids": ["list of substrate IDs for this group"],
  "product_ids": ["list of product IDs for this group"],
  "confidence": 0-100,
  "evidence": "text supporting this substrate/product assignment"
}}

CRITICAL OUTPUT REQUIREMENT:
Respond ONLY with valid JSON. NO markdown fences, no commentary, no explanations.
Start directly with { and end with }
""")

PROMPT_COMPOUND_MAPPING = dedent("""
Extract compound identifiers and their IUPAC names from the provided sections.

Look for ALL compounds mentioned, including:
1. Compounds with explicit IUPAC names in the text
2. Common reagents where you can provide standard IUPAC names
3. Products that may not be explicitly characterized

CRITICAL - NO HALLUCINATION:
- Extract IUPAC names EXACTLY as written in the source
- DO NOT modify, correct, or "improve" any chemical names
- If a name is written as "benzyl-2-phenylcyclopropane-1-carboxylate", keep it exactly
- Only provide standard IUPAC names for common reagents if not found in text
- If no IUPAC name is found for a compound, return null for iupac_name
- Include ALL compounds found or referenced

IMPORTANT - ONE NAME PER COMPOUND:
- Return ONLY ONE IUPAC name per compound identifier
- If multiple names are found for the same compound, choose the one most likely to be the IUPAC name:
  1. Names explicitly labeled as "IUPAC name:" in the text
  2. Names in compound characterization sections
  3. The most systematic/complete chemical name
- Do NOT return multiple IUPAC names in a single iupac_name field

Return as JSON:
{
  "compound_mappings": [
    {
      "identifier": "compound identifier",
      "iupac_name": "complete IUPAC name",
      "common_names": ["any alternative names"],
      "compound_type": "substrate/product/reagent/other",
      "source_location": "where found or inferred"
    }
  ]
}
""")

###############################################################################
# 6 - EXTRACTION ENGINE
###############################################################################

class ReactionExtractor:
    _FIG_RE = re.compile(r"(?:supplementary\s+)?fig(?:ure)?\.?\s+s?\d+[a-z]?", re.I)
    _TAB_RE = re.compile(r"(?:supplementary\s+)?tab(?:le)?\s+s?\d+[a-z]?", re.I)

    def __init__(self, manuscript: Path, si: Optional[Path], cfg: Config, debug_dir: Optional[Path] = None, 
                 campaign_filter: Optional[str] = None, all_campaigns: Optional[List[str]] = None,
                 campaign_info: Optional[Dict[str, Any]] = None):
        self.manuscript = manuscript
        self.si = si
        self.cfg = cfg
        self.model = get_model(cfg)
        self.debug_dir = debug_dir
        self.campaign_filter = campaign_filter  # Filter for specific campaign
        self.all_campaigns = all_campaigns or []  # List of all campaigns for context
        self.campaign_info = campaign_info  # Detailed campaign information from campaigns.json
        
        # Store PDF paths for direct PDF access
        self.ms_pdf_path = manuscript
        self.si_pdf_path = si
        
        # Cache for extracted figures to avoid redundant extractions (bounded to prevent memory leaks)
        self._figure_cache = LRUCache(maxsize=100)  # Figures are large, so smaller cache
        self._model_reaction_locations_cache = LRUCache(maxsize=50)
        
        # Cache for compound mappings to avoid repeated API calls (bounded to prevent memory leaks)
        self._compound_mapping_cache = LRUCache(maxsize=1000)
        self._compound_mapping_text_cache = LRUCache(maxsize=500)  # Cache text extractions too
        
        # Cache for reaction locations to avoid repeated API calls (bounded to prevent memory leaks)
        self._reaction_locations_cache = LRUCache(maxsize=50)
        
        # Create debug directory if specified
        if self.debug_dir:
            self.debug_dir = Path(self.debug_dir)
            self.debug_dir.mkdir(parents=True, exist_ok=True)
            LOGGER.info("Debug output will be saved to: %s", self.debug_dir)
        
        if self.campaign_filter:
            LOGGER.info("Filtering extraction for campaign: %s", self.campaign_filter)

        # Preload text pages
        LOGGER.info("Reading PDFs…")
        self.ms_pages = extract_text_by_page(manuscript)
        self.si_pages = extract_text_by_page(si)
        self.all_pages = self.ms_pages + self.si_pages

        # Keep open fitz Docs for image extraction
        self.ms_doc = fitz.open(str(manuscript))
        self.si_doc = fitz.open(str(si)) if si else None

    # ------------------------------------------------------------------
    # 6.1 Find locations (unchanged)
    # ------------------------------------------------------------------

    def _collect_captions_and_titles(self) -> str:
        # Combine full manuscript and SI text
        sections = []
        
        # Add manuscript content
        if self.ms_pages:
            ms_text = "\n".join(self.ms_pages)
            sections.append("=== MAIN MANUSCRIPT ===\n" + ms_text)
            LOGGER.debug("Added manuscript text: %d chars", len(ms_text))
        
        # Add full SI content
        if self.si_pages:
            si_text = "\n".join(self.si_pages)
            sections.append("\n\n=== SUPPORTING INFORMATION ===\n" + si_text)
            LOGGER.debug("Added SI text: %d chars", len(si_text))
        
        result = "\n".join(sections)
        total_chars = len(result)
        
        LOGGER.info("Sending full manuscript + SI for find_locations: %d total chars", total_chars)
        
        # Warn if it's getting too large
        if total_chars > 200000:
            LOGGER.warning("Combined text is large (%d chars), may approach token limits", total_chars)
        
        return result

    def find_reaction_locations(self) -> List[Dict[str, Any]]:
        """Find all locations containing reaction performance data."""
        # Create cache key based on campaign filter
        cache_key = f"locations_{self.campaign_filter or 'all'}"
        
        # Check cache first
        cached_result = self._reaction_locations_cache.get(cache_key)
        if cached_result is not None:
            LOGGER.info("Using cached reaction locations for campaign: %s", self.campaign_filter or 'all')
            return cached_result
        
        # Add campaign context - always provide context to help model understanding
        campaign_context = ""
        
        # If we have detailed campaign info, use it to provide specific guidance
        if self.campaign_info:
            location_hints = get_location_hints_for_campaign(self.campaign_info)
            campaign_context = f"""
            IMPORTANT: You are looking for performance data specifically for the {self.campaign_filter} campaign.
            
            CAMPAIGN DETAILS FROM CAMPAIGNS.JSON:
            - Campaign ID: {self.campaign_info.get('campaign_id', '')}
            - Name: {self.campaign_info.get('campaign_name', '')}
            - Description: {self.campaign_info.get('description', '')}
            - Model Substrate: {self.campaign_info.get('model_substrate', '')} (ID: {self.campaign_info.get('substrate_id', '')})
            - Model Product: {self.campaign_info.get('model_product', '')} (ID: {self.campaign_info.get('product_id', '')})
            - Notes: {self.campaign_info.get('notes', '')}
            
            KNOWN DATA LOCATIONS FOR THIS CAMPAIGN: {', '.join(location_hints)}
            These locations are known to contain relevant data - prioritize them highly.
            
            CRITICAL REQUIREMENT: For this campaign, you must find locations that contain COMPLETE EVOLUTION LINEAGE DATA.
            - Look for data showing the entire evolutionary progression of enzyme variants
            - Prioritize locations that show performance data for ALL variants in the lineage
            - The campaign description and notes above provide context about the evolution strategy used
            
            {f"ALL CAMPAIGNS IN THIS PAPER: {chr(10).join([f'- {c}' for c in self.all_campaigns])}" if self.all_campaigns else ""}
            
            CRITICAL: Only return locations that contain data for this specific campaign.
            """
        elif self.campaign_filter:
            campaigns_warning = ""
            if self.all_campaigns:
                campaigns_warning = f"""
            ALL CAMPAIGNS IN THIS PAPER:
            {chr(10).join([f"- {campaign}" for campaign in self.all_campaigns])}

            CRITICAL WARNING: Do NOT confuse campaigns! Each campaign uses completely different substrates.
            Be extremely careful to only extract data for the {self.campaign_filter} campaign.
            """
            
            campaign_context = f"""
            IMPORTANT: You are looking for performance data specifically for the {self.campaign_filter} campaign.
            Only return locations that contain data for this specific campaign.
            Ignore locations that contain data for other campaigns.
            {campaigns_warning}

            """
        else:
            # Even for single campaigns, provide context about what to look for
            campaign_context = f"""
            IMPORTANT: You are looking for performance data showing enzyme evolution progression.
            Look for locations that contain actual performance metrics (yield, TTN, TON, activity, etc.) 
            for multiple enzyme variants, not just mutation lists or method descriptions.

            Tables may only contain mutation information without performance data - check the actual 
            table content below the caption to verify if performance metrics are present.
            Figures with evolutionary lineage data often contain the actual performance matrix.

            """
        
        prompt = campaign_context + PROMPT_FIND_LOCATIONS + "\n\n" + self._collect_captions_and_titles()
        try:
            data = generate_json_with_retry(
                self.model,
                prompt,
                temperature=self.cfg.location_temperature,
                debug_dir=self.debug_dir,
                tag="find_locations"
            )
            # Handle both single dict (backwards compatibility) and list
            result = []
            if isinstance(data, dict):
                result = [data]
            elif isinstance(data, list):
                result = data
            else:
                LOGGER.error("Expected list or dict from Gemini, got: %s", type(data))
                result = []
            
            # Cache the result
            self._reaction_locations_cache.put(cache_key, result)
            LOGGER.info("Cached reaction locations for campaign: %s", self.campaign_filter or 'all')
            
            return result
        except Exception as e:
            LOGGER.error("Failed to find reaction locations: %s", e)
            return []

    def _get_base_location(self, location: str) -> str:
        """Extract the base location identifier (e.g., 'Table S1' from 'Table S1' or 'S41-S47').
        
        This helps group related locations that likely share the same model reaction.
        """
        # Common patterns for locations
        patterns = [
            (r'Table\s+S\d+', 'table'),
            (r'Figure\s+S\d+', 'figure'),
            (r'Table\s+\d+', 'table'),
            (r'Figure\s+\d+', 'figure'),
            (r'S\d+(?:-S\d+)?', 'supp'),  # Supplementary pages like S41-S47
        ]
        
        for pattern, loc_type in patterns:
            match = re.search(pattern, location, re.I)
            if match:
                return match.group(0)
        
        # Default: use the location as-is
        return location

    def analyze_lineage_groups(self, locations: List[Dict[str, Any]], enzyme_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze if there are distinct lineage groups based on different locations.
        
        Key principle: Different locations (tables/figures) indicate different model reactions.
        """
        # Group locations by their base identifier
        location_groups = {}
        
        for loc in locations:
            location_id = loc['location']
            base_location = self._get_base_location(location_id)
            
            if base_location not in location_groups:
                location_groups[base_location] = []
            location_groups[base_location].append(loc)
        
        # Each unique base location represents a potential lineage group
        lineage_groups = []
        
        for base_loc, locs in location_groups.items():
            # Use the location with highest confidence as primary
            primary_loc = max(locs, key=lambda x: x.get('confidence', 0))
            
            # Create a group for this location
            group = {
                'group_id': base_loc,
                'data_location': primary_loc['location'],
                'all_locations': [l['location'] for l in locs],
                'lineage_hint': primary_loc.get('lineage_hint', ''),
                'caption': primary_loc.get('caption', ''),
                'confidence': primary_loc.get('confidence', 0)
            }
            lineage_groups.append(group)
        
        # Multiple distinct base locations = multiple model reactions
        has_multiple = len(location_groups) > 1
        
        LOGGER.info("Location-based lineage analysis: %d distinct base locations found", 
                   len(location_groups))
        for group in lineage_groups:
            LOGGER.info("  - %s: %s", group['group_id'], group['data_location'])
        
        return {
            'has_multiple_lineages': has_multiple,
            'lineage_groups': lineage_groups,
            'confidence': 95
        }
    
    def find_lineage_model_reaction(self, location: str, group_context: str, model_reaction_locations: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Find the model reaction for a specific lineage group.
        Returns early if no relevant text is found to avoid unnecessary API calls."""
        
        # Gather relevant text near this location
        page_text = self._page_with_reference(location) or ""
        
        # Early exit if no text found for this location
        if not page_text or len(page_text.strip()) < 100:
            LOGGER.info("No sufficient text found for location %s, skipping lineage-specific extraction", location)
            return {}
        
        # Also check manuscript introduction for model reaction info
        intro_text = "\n\n".join(self.ms_pages[:3]) if self.ms_pages else ""
        
        # Quick relevance check - look for reaction-related keywords
        reaction_keywords = ["substrate", "product", "reaction", "compound", "synthesis", "procedure", "method"]
        combined_text = (page_text + intro_text).lower()
        if not any(keyword in combined_text for keyword in reaction_keywords):
            LOGGER.info("No reaction-related keywords found for location %s, skipping lineage extraction", location)
            return {}
        
        # Build the prompt with location and context
        prompt = PROMPT_FIND_LINEAGE_MODEL_REACTION.format(
            location=location,
            group_context=group_context
        )
        prompt += f"\n\nText near {location}:\n{page_text[:3000]}"
        prompt += f"\n\nManuscript introduction:\n{intro_text[:3000]}"
        
        # If we have model reaction locations, include text from those locations too
        text_added = False
        if model_reaction_locations:
            # Add text from model reaction location
            if model_reaction_locations.get("model_reaction_location", {}).get("location"):
                model_loc = model_reaction_locations["model_reaction_location"]["location"]
                model_text = self._get_text_around_location(model_loc)
                if model_text:
                    prompt += f"\n\nText from {model_loc} (potential model reaction location):\n{model_text[:3000]}"
                    text_added = True
            
            # Add text from conditions location (often contains reaction details)
            if model_reaction_locations.get("conditions_location", {}).get("location"):
                cond_loc = model_reaction_locations["conditions_location"]["location"]
                cond_text = self._get_text_around_location(cond_loc)
                if cond_text:
                    prompt += f"\n\nText from {cond_loc} (reaction conditions):\n{cond_text[:3000]}"
                    text_added = True
        
        # If we didn't find any model reaction locations and the page text is sparse, skip
        if not text_added and len(page_text.strip()) < 500:
            LOGGER.info("Insufficient context for lineage model reaction extraction at %s", location)
            return {}
        
        try:
            LOGGER.info("Attempting lineage-specific model reaction extraction for %s", location)
            data = generate_json_with_retry(
                self.model,
                prompt,
                temperature=self.cfg.model_reaction_temperature,
                debug_dir=self.debug_dir,
                tag=f"lineage_model_reaction_{location.replace(' ', '_')}"
            )
            
            # Validate the response has useful information
            if isinstance(data, dict) and (data.get('substrate_ids') or data.get('product_ids')):
                LOGGER.info("Lineage model reaction extraction successful for %s", location)
                return data
            else:
                LOGGER.info("Lineage model reaction extraction returned empty results for %s", location)
                return {}
                
        except Exception as e:
            LOGGER.error("Failed to find model reaction for lineage at %s: %s", location, e)
            return {}

    # ------------------------------------------------------------------
    # 6.2 Figure / Table context helpers
    # ------------------------------------------------------------------

    def _is_toc_page(self, page_text: str) -> bool:
        """Detect if a page is a Table of Contents page."""
        # Look for common TOC indicators
        toc_indicators = [
            "table of contents",
            "contents",
            r"\.{5,}",  # Multiple dots (common in TOCs)
            r"\d+\s*\n\s*\d+\s*\n\s*\d+",  # Multiple page numbers in sequence
        ]
        
        # Count how many TOC-like patterns we find
        toc_score = 0
        text_lower = page_text.lower()
        
        # Check for explicit TOC title
        if "table of contents" in text_lower or (
            "contents" in text_lower and text_lower.index("contents") < 200
        ):
            toc_score += 3
        
        # Check for multiple figure/table references with page numbers
        figure_with_page = re.findall(r'figure\s+[sS]?\d+.*?\.{2,}.*?\d+', text_lower)
        table_with_page = re.findall(r'table\s+[sS]?\d+.*?\.{2,}.*?\d+', text_lower)
        
        if len(figure_with_page) + len(table_with_page) > 5:
            toc_score += 2
        
        # Check for many dotted lines
        if len(re.findall(r'\.{5,}', page_text)) > 3:
            toc_score += 1
            
        return toc_score >= 2

    def _build_caption_index(self) -> Dict[str, Dict[str, Any]]:
        """Build an index of all captions for quick lookup."""
        if hasattr(self, '_caption_index'):
            return self._caption_index
            
        cap_pattern = get_universal_caption_pattern()
        caption_index = {}
        
        for idx, page in enumerate(self.all_pages):
            source = "manuscript" if idx < len(self.ms_pages) else "supplementary"
            page_num = idx + 1 if idx < len(self.ms_pages) else idx - len(self.ms_pages) + 1
            
            for match in cap_pattern.finditer(page):
                caption_text = match.group(0).strip()
                # Extract a normalized key (e.g., "table 5", "figure 3")
                caption_lower = caption_text.lower()
                
                # Store multiple access patterns for the same caption
                caption_info = {
                    'full_caption': caption_text,
                    'page_content': page,
                    'page_idx': idx,
                    'source': source,
                    'page_num': page_num,
                    'match_start': match.start()
                }
                
                # Create multiple keys for flexible matching
                # Key 1: Full caption text (first 100 chars)
                key1 = caption_text[:100].lower().strip()
                caption_index[key1] = caption_info
                
                # Key 2: Simplified reference (e.g., "table 5", "figure s3")
                ref_match = re.search(r'(table|figure|fig|scheme)\s*s?(\d+[a-z]?)', caption_lower)
                if ref_match:
                    key2 = f"{ref_match.group(1)} {ref_match.group(2)}"
                    caption_index[key2] = caption_info
                    
                    # Also store with 's' prefix if in SI
                    if source == "supplementary" and 's' not in key2:
                        key3 = f"{ref_match.group(1)} s{ref_match.group(2)}"
                        caption_index[key3] = caption_info
        
        self._caption_index = caption_index
        return caption_index
    
    def _page_with_reference(self, ref_id: str) -> Optional[str]:
        """Find page(s) containing a reference using flexible matching."""
        caption_index = self._build_caption_index()
        ref_lower = ref_id.lower().strip()
        
        # Try multiple matching strategies
        matches = []
        
        # Strategy 1: Direct key lookup
        if ref_lower in caption_index:
            matches.append(caption_index[ref_lower])
        
        # Strategy 2: Fuzzy matching for section titles and other references
        # Remove extra spaces, handle PDF extraction artifacts
        ref_words = set(ref_lower.replace('.', ' ').split()) - {'and', 'the', 'for', 'of', 'in', 'a', 'to', 'with'}
        if len(ref_words) >= 2:  # Need at least 2 meaningful words
            best_match_score = 0
            best_match_value = None
            
            for key, value in caption_index.items():
                # Normalize the key similar to ref
                key_words = set(key.replace('.', ' ').split()) - {'and', 'the', 'for', 'of', 'in', 'a', 'to', 'with'}
                
                # Calculate match score
                if len(key_words) > 0 and len(ref_words) > 0:
                    common_words = ref_words.intersection(key_words)
                    score = len(common_words) / min(len(ref_words), len(key_words))
                    
                    # Accept matches with 60% or higher similarity
                    if score >= 0.6 and score > best_match_score:
                        best_match_score = score
                        best_match_value = value
            
            if best_match_value:
                LOGGER.info("Fuzzy matched '%s' with score %.2f", ref_id, best_match_score)
                matches.append(best_match_value)
        
        # Strategy 3: Normalized reference lookup (e.g., "table 5", "figure s3")
        ref_match = re.match(r'(table|figure|fig|scheme)\s*s?(\d+[a-z]?)', ref_lower, re.I)
        if ref_match:
            ref_type, ref_num = ref_match.groups()
            if ref_type == 'fig':
                ref_type = 'figure'
            
            # Try different key formats
            keys_to_try = [
                f"{ref_type} {ref_num}",
                f"{ref_type} s{ref_num}",
                f"table {ref_num}",  # Sometimes figures are mislabeled
                f"fig {ref_num}",
                f"figure {ref_num}"
            ]
            
            for key in keys_to_try:
                if key in caption_index and caption_index[key] not in matches:
                    matches.append(caption_index[key])
        
        # Strategy 3: Fuzzy matching on caption text
        if not matches:
            # Look for any caption containing the reference number
            for key, info in caption_index.items():
                if ref_match and ref_num in key and any(t in key for t in ['table', 'figure', 'fig', 'scheme']):
                    if info not in matches:
                        matches.append(info)
        
        # Return results
        if not matches:
            LOGGER.warning(f"No matches found for reference '{ref_id}'")
            # Last resort: simple text search
            for page in self.all_pages:
                if ref_lower in page.lower():
                    return page
            return None
        
        # If single match, return it
        if len(matches) == 1:
            return matches[0]['page_content']
        
        # Multiple matches: combine them with source annotations
        LOGGER.info(f"Found {len(matches)} potential matches for '{ref_id}'")
        combined_pages = []
        for match in matches:
            header = f"\n\n=== {match['source'].upper()} PAGE {match['page_num']} ===\n"
            header += f"Caption: {match['full_caption'][:200]}...\n"
            combined_pages.append(header + match['page_content'])
        
        return "\n".join(combined_pages)

    # ---- Table text helper - now returns full page ----
    def _extract_table_context(self, ref: str) -> str:
        page = self._page_with_reference(ref)
        if not page:
            return ""
        # Return the entire page content for better table extraction
        return page

    # ---- Figure caption helper (text fallback) ----
    def _extract_figure_caption(self, ref: str) -> str:
        page = self._page_with_reference(ref)
        if not page:
            return ""
        m = re.search(rf"({re.escape(ref)}[\s\S]{{0,800}}?\.)", page, re.I)
        if m:
            return m.group(1)
        for line in page.split("\n"):
            if ref.lower() in line.lower():
                return line
        return page[:800]

    def _ensure_rgb_pixmap(self, pix: fitz.Pixmap) -> fitz.Pixmap:
        """Ensure pixmap is in RGB colorspace for PIL compatibility."""
        if pix.alpha:  # RGBA -> RGB
            pix = fitz.Pixmap(fitz.csRGB, pix)
        elif pix.colorspace and pix.colorspace.name not in ["DeviceRGB", "DeviceGray"]:
            # Convert unsupported colorspaces (CMYK, LAB, etc.) to RGB
            pix = fitz.Pixmap(fitz.csRGB, pix)
        return pix

    # ---- NEW: Page image helper for both figures and tables ----
    def _extract_page_png(self, ref: str, extract_figure_only: bool = True, caption_hint: str = "", document_hint: str = "") -> Optional[str]:
        """Export the page containing the reference as PNG.
        If extract_figure_only=True, extracts just the figure above the caption.
        If False, extracts the entire page (useful for tables).
        Returns a base64-encoded PNG or None.
        
        Args:
            ref: The reference string (e.g., "Fig. 3")
            extract_figure_only: Whether to extract just the figure or the entire page
            caption_hint: Optional caption text from location data to help find the exact figure
            document_hint: Optional hint about which document to search ("manuscript" or "supplementary")
        """
        LOGGER.info("_extract_page_png called with ref='%s', extract_figure_only=%s, caption_hint='%s', document_hint='%s'", 
                    ref, extract_figure_only, caption_hint[:50] + "..." if caption_hint else "EMPTY", document_hint)
        
        # Check cache first - include document hint in key to avoid cross-document contamination
        cache_key = f"{ref}_{extract_figure_only}_{document_hint}" if document_hint else f"{ref}_{extract_figure_only}"
        cached_result = self._figure_cache.get(cache_key)
        if cached_result is not None:
            LOGGER.info("Using cached figure for %s (cache key: %s)", ref, cache_key)
            return cached_result
        else:
            LOGGER.info("Cache miss for %s (cache key: %s)", ref, cache_key)
        
        # For table extraction, use multi-page approach
        if not extract_figure_only:
            pages_with_ref = self._find_pages_with_reference(ref)
            if pages_with_ref:
                LOGGER.debug(f"Found {len(pages_with_ref)} pages containing {ref}")
                return self._extract_multiple_pages_png(pages_with_ref, ref)
            return None

        # For figure extraction, prioritize based on document hint
        if document_hint == "manuscript" and self.ms_doc:
            # Search manuscript first, then SI as fallback
            docs = list(filter(None, [self.ms_doc, self.si_doc]))
            LOGGER.info("Prioritizing manuscript document for '%s' (hint: %s)", ref, document_hint)
            LOGGER.info("Search order: 1) Manuscript, 2) SI (fallback)")
        elif document_hint == "supplementary" and self.si_doc:
            # Search SI first, then manuscript as fallback
            docs = list(filter(None, [self.si_doc, self.ms_doc]))
            LOGGER.info("Prioritizing supplementary document for '%s' (hint: %s)", ref, document_hint)
            LOGGER.info("Search order: 1) SI, 2) Manuscript (fallback)")
        else:
            # Default behavior - search both in order
            docs = list(filter(None, [self.ms_doc, self.si_doc]))
            LOGGER.info("Searching for '%s' in %d documents (no document hint)", ref, len(docs))
            LOGGER.info("Search order: 1) Manuscript, 2) SI (default order)")
        
        for doc_idx, doc in enumerate(docs):
            # Determine document name based on actual document, not position
            doc_name = "MS" if doc == self.ms_doc else "SI"
            LOGGER.info("Searching document %d/%d: %s (has %d pages)", 
                       doc_idx + 1, len(docs), doc_name, doc.page_count)
            
            for page_number in range(doc.page_count):
                page = doc.load_page(page_number)
                page_text = page.get_text()
                LOGGER.debug("Checking page %d of %s document (text length: %d chars)", 
                           page_number + 1, doc_name, len(page_text))
                
                # Skip Table of Contents pages
                if self._is_toc_page(page_text):
                    LOGGER.debug("Skipping page %d - detected as Table of Contents", page_number + 1)
                    continue
                
                # If we have a caption hint, try to find it using fuzzy matching
                if caption_hint:
                    LOGGER.info("=== CAPTION HINT SEARCH ===")
                    LOGGER.info("Caption hint provided: %s", caption_hint[:100])
                    LOGGER.info("Searching in %s document, page %d", doc_name, page_number + 1)
                    LOGGER.info("Page text length: %d chars", len(page_text))
                    
                    # Check if caption exists in raw form
                    if caption_hint[:50] in page_text:
                        LOGGER.info("✓ Caption hint found in raw page text!")
                    else:
                        LOGGER.info("✗ Caption hint NOT found in raw page text")
                    
                    # Normalize texts for better matching
                    def normalize_for_matching(text):
                        # Remove extra whitespace, normalize spaces around punctuation
                        text = ' '.join(text.split())
                        # Normalize different dash types
                        text = text.replace('–', '-').replace('—', '-')
                        # Normalize pipe character and other special chars
                        text = text.replace('|', ' ').replace('│', ' ')
                        # Remove multiple spaces
                        text = ' '.join(text.split())
                        return text
                    
                    normalized_hint = normalize_for_matching(caption_hint[:100])  # Use first 100 chars
                    normalized_page = normalize_for_matching(page_text)
                    
                    # Try to find the caption using fuzzy matching
                    best_match_pos = -1
                    best_match_score = 0
                    match_found = False
                    
                    # Slide through the page text looking for best match
                    hint_len = len(normalized_hint)
                    for i in range(len(normalized_page) - hint_len + 1):
                        snippet = normalized_page[i:i + hint_len]
                        # Simple character-based similarity
                        matches = sum(1 for a, b in zip(normalized_hint, snippet) if a == b)
                        score = matches / hint_len
                        
                        if score > best_match_score and score > 0.8:  # 80% similarity threshold
                            best_match_score = score
                            best_match_pos = i
                            match_found = True
                    
                    if match_found and best_match_pos >= 0:
                        LOGGER.info("Found caption match in %s document on page %d with %.1f%% similarity", 
                                   doc_name, page_number + 1, best_match_score * 100)
                        
                        # Instead of complex position mapping, just search for the beginning of the caption
                        # Use the first 30 chars which should be unique enough
                        search_text = caption_hint[:30].strip()
                        LOGGER.info("Searching for caption text: '%s'", search_text)
                        caption_instances = page.search_for(search_text)
                        LOGGER.info("Found %d caption instances", len(caption_instances) if caption_instances else 0)
                        
                        if caption_instances:
                            cap_rect = caption_instances[0]
                            caption_found = True
                            # Extract figure above this caption
                            if extract_figure_only:
                                LOGGER.info("Extracting figure area including caption for %s from %s document", ref, doc_name)
                                LOGGER.info("Caption found at rect: %s on page %d", cap_rect, page_number + 1)
                                page_rect = page.rect
                                
                                # Include the caption in the extraction
                                # Add some padding below the caption to ensure we get the full text
                                caption_padding = 30  # pixels below caption
                                figure_rect = fitz.Rect(0, 0, page_rect.width, cap_rect.y1 + caption_padding)
                                LOGGER.info("Page rect: %s, Figure rect including caption: %s", page_rect, figure_rect)
                                mat = fitz.Matrix(5.0, 5.0)
                                pix = page.get_pixmap(matrix=mat, clip=figure_rect)
                                pix = self._ensure_rgb_pixmap(pix)
                                img_bytes = pix.tobytes("png")
                                img_b64 = b64encode(img_bytes).decode('utf-8')
                                self._figure_cache.put(cache_key, img_b64)
                                LOGGER.info("Successfully extracted figure using caption hint for %s from %s document, page %d", 
                                           ref, doc_name, page_number + 1)
                                return img_b64
                    else:
                        LOGGER.info("No fuzzy match found for caption hint on page %d (best score: %.1f%%)", 
                                   page_number + 1, best_match_score * 100)
                
                # If caption hint didn't work or wasn't provided, fall back to pattern matching
                # Look for figure caption pattern more flexibly
                # Normalize the reference to handle variations
                figure_num = ref.replace('Figure', '').replace('figure', '').replace('Fig.', '').replace('Fig', '').strip()
                
                # Extract main figure number from subfigure (e.g., "1C" -> "1")
                main_figure_num = re.match(r'^(\d+)', figure_num)
                if main_figure_num:
                    main_figure_num = main_figure_num.group(1)
                else:
                    main_figure_num = figure_num
                
                # Create a flexible pattern that handles various spacing and formatting
                # This pattern looks for "Figure" or "Fig" (case insensitive) followed by optional spaces
                # then the figure number, then any of: period, colon, pipe, space+capital letter, or end of line
                # Also match at the beginning of a line to catch captions
                flexible_pattern = rf"(?i)(?:^|\n)\s*(?:figure|fig\.?)\s*{re.escape(main_figure_num)}(?:\.|:|\||\s+\||(?=\s+[A-Z])|\s*$)"
                
                LOGGER.debug("Looking for figure caption '%s' with flexible pattern: %s", 
                           main_figure_num, flexible_pattern)
                
                caption_found = False
                cap_rect = None
                
                # Search for all matches of the flexible pattern
                for match in re.finditer(flexible_pattern, page_text, re.MULTILINE):
                    LOGGER.debug("Found potential figure caption: %s at position %d", match.group(0), match.start())
                    # Check if this is likely an actual caption (not just a reference)
                    match_start = match.start()
                    match_end = match.end()
                    
                    # Get surrounding context
                    context_start = max(0, match_start - 50)
                    context_end = min(len(page_text), match_end + 100)
                    context = page_text[context_start:context_end]
                    
                    # Check if this looks like a real caption (not just a reference)
                    # Look for words that typically precede figure references
                    preceding_text = page_text[max(0, match_start-20):match_start].lower()
                    if any(word in preceding_text for word in ['see ', 'in ', 'from ', 'shown in ', 'refer to ']):
                        LOGGER.debug("Skipping reference preceded by: %s", preceding_text.strip())
                        continue
                    
                    # Check if there's descriptive text after the figure number
                    remaining_text = page_text[match_end:match_end+100].strip()
                    
                    # For actual captions, there should be substantial descriptive text
                    if len(remaining_text) < 20:
                        LOGGER.debug("Skipping potential reference: insufficient text after (%d chars)", len(remaining_text))
                        continue
                        
                    # Check if the remaining text looks like a caption (contains descriptive words)
                    # Expanded list of caption keywords to be more inclusive
                    first_words = remaining_text[:50].lower()
                    caption_keywords = ['detailed', 'representative', 'shows', 'comparison', 
                                      'illustrates', 'demonstrates', 'results', 'data',
                                      'chromatogram', 'spectra', 'analysis', 'site-directed',
                                      'mutagenesis', 'mutants', 'evolution', 'directed',
                                      'screening', 'reaction', 'variant', 'enzyme', 'protein',
                                      'activity', 'performance', 'yield', 'selectivity',
                                      'characterization', 'optimization', 'development',
                                      'structure', 'domain', 'crystal', 'model']
                    if not any(word in first_words for word in caption_keywords):
                        LOGGER.debug("Skipping: doesn't look like caption text: %s", first_words)
                        continue
                    
                    # Found actual figure caption, get its position
                    caption_text = match.group(0)
                    text_instances = page.search_for(caption_text, quads=False)
                    if text_instances:
                        cap_rect = text_instances[0]
                        caption_found = True
                        LOGGER.info("Found actual caption for %s in %s document on page %d: '%s' with following text: '%s...'", 
                                  ref, doc_name, page_number + 1, caption_text, remaining_text[:50])
                        break
                
                if not caption_found:
                    # Debug: show what figure-related text is actually on this page
                    figure_mentions = [line.strip() for line in page_text.split('\n') 
                                     if 'figure' in line.lower() and main_figure_num.lower() in line.lower()]
                    if figure_mentions:
                        LOGGER.debug("Page %d has figure mentions but no caption match: %s", 
                                   page_number, figure_mentions[:3])
                    
                    # For supplementary figures, also check for "supplementary" mentions
                    if 'supplementary' in ref.lower():
                        supp_mentions = [line.strip() for line in page_text.split('\n')
                                       if 'supplementary' in line.lower() and 'figure' in line.lower()]
                        if supp_mentions:
                            LOGGER.warning("Found supplementary figure mentions on page %d but no caption match. First 3: %s", 
                                         page_number + 1, supp_mentions[:3])
                    continue
                
                if extract_figure_only:
                    # Extract the figure area including the caption
                    LOGGER.info("Extracting figure area including caption for %s", ref)
                    
                    # Get the page dimensions
                    page_rect = page.rect
                    
                    # Extract the area including the caption
                    if cap_rect:
                        # Extract from top of page to bottom of caption plus padding
                        caption_padding = 30  # pixels below caption
                        figure_rect = fitz.Rect(0, 0, page_rect.width, cap_rect.y1 + caption_padding)
                        LOGGER.debug("Extracting figure area with caption: %s (caption ends at y=%f)", figure_rect, cap_rect.y1)
                    else:
                        # If no caption found, use top 80% of page
                        figure_rect = fitz.Rect(0, 0, page_rect.width, page_rect.height * 0.8)
                        LOGGER.debug("No caption found, using top 80% of page: %s", figure_rect)
                    
                    # Extract the figure area only
                    mat = fitz.Matrix(5.0, 5.0)  # 5x zoom for better quality
                    pix = page.get_pixmap(matrix=mat, clip=figure_rect)
                    pix = self._ensure_rgb_pixmap(pix)
                    img_bytes = pix.tobytes("png")
                    
                    # Save PNG to debug directory if available
                    if self.debug_dir:
                        timestamp = int(time.time())
                        png_file = self.debug_dir / f"figure_{ref.replace(' ', '_')}_{timestamp}.png"
                        with open(png_file, 'wb') as f:
                            f.write(img_bytes)
                        LOGGER.info("Saved figure page to: %s", png_file)
                    
                    result = b64encode(img_bytes).decode()
                    # Cache the result
                    self._figure_cache.put(cache_key, result)
                    return result
                else:
                    # Extract the entire page as an image
                    mat = fitz.Matrix(5.0, 5.0)  # 5x zoom for better quality
                    pix = page.get_pixmap(matrix=mat)
                    pix = self._ensure_rgb_pixmap(pix)
                    img_bytes = pix.tobytes("png")
                    
                    # Save PNG to debug directory if available
                    if self.debug_dir:
                        timestamp = int(time.time())
                        png_file = self.debug_dir / f"page_{ref.replace(' ', '_')}_{timestamp}.png"
                        with open(png_file, 'wb') as f:
                            f.write(img_bytes)
                        LOGGER.info("Saved page image to: %s", png_file)
                    
                    result = b64encode(img_bytes).decode()
                    # Cache the result
                    self._figure_cache.put(cache_key, result)
                    return result
        
        # Fallback: If no caption found, try to find any page that mentions this figure
        LOGGER.info("No figure caption found for '%s', trying fallback search", ref)
        
        for doc_idx, doc in enumerate(docs):
            doc_name = "MS" if doc_idx == 0 else "SI"
            for page_number in range(doc.page_count):
                page = doc.load_page(page_number)
                page_text = page.get_text()
                
                # Look for any mention of the figure reference
                if re.search(rf'\b{re.escape(ref)}\b', page_text, re.IGNORECASE):
                    LOGGER.info("Found '%s' mentioned on page %d of %s document (fallback)", 
                               ref, page_number + 1, doc_name)
                    
                    # Extract the entire page as the figure might be on this page
                    mat = fitz.Matrix(5.0, 5.0)  # 5x zoom for better quality
                    pix = page.get_pixmap(matrix=mat)
                    pix = self._ensure_rgb_pixmap(pix)
                    img_bytes = pix.tobytes("png")
                    
                    # Save PNG to debug directory if available
                    if self.debug_dir:
                        timestamp = int(time.time())
                        png_file = self.debug_dir / f"fallback_{ref.replace(' ', '_')}_{timestamp}.png"
                        with open(png_file, 'wb') as f:
                            f.write(img_bytes)
                        LOGGER.info("Saved fallback page image to: %s", png_file)
                    
                    result = b64encode(img_bytes).decode()
                    # Cache the result
                    self._figure_cache.put(cache_key, result)
                    return result
        
        LOGGER.warning("_extract_page_png returning None for '%s' - figure not found in any document", ref)
        return None
    
    def _find_pages_with_reference(self, ref: str) -> List[Tuple[fitz.Document, int]]:
        """Find all pages containing the reference across documents.
        Prioritizes pages with actual captions over just references.
        Returns list of (document, page_number) tuples."""
        pages_found = []
        caption_pages = []
        
        for doc in filter(None, [self.ms_doc, self.si_doc]):
            for page_number in range(doc.page_count):
                page = doc.load_page(page_number)
                page_text = page.get_text()
                
                # Skip Table of Contents pages
                if self._is_toc_page(page_text):
                    LOGGER.debug("Skipping TOC page %d in _find_pages_with_reference", page_number + 1)
                    continue
                
                # Check for actual figure caption first
                if ref.lower().startswith('figure'):
                    figure_num = ref.replace('Figure ', '').replace('figure ', '')
                    
                    # Extract main figure number from subfigure (e.g., "1C" -> "1")
                    main_figure_num = re.match(r'^(\d+)', figure_num)
                    if main_figure_num:
                        main_figure_num = main_figure_num.group(1)
                    else:
                        main_figure_num = figure_num
                    
                    caption_patterns = [
                        rf"^Figure\s+{re.escape(main_figure_num)}\.",
                        rf"^Figure\s+{re.escape(main_figure_num)}:",
                        rf"^Figure\s+{re.escape(main_figure_num)}\s+[A-Z]"
                    ]
                    
                    for pattern in caption_patterns:
                        if re.search(pattern, page_text, re.MULTILINE | re.IGNORECASE):
                            caption_pages.append((doc, page_number))
                            break
                
                # Fallback to any mention of the reference
                if ref.lower() in page_text.lower():
                    pages_found.append((doc, page_number))
        
        # Return caption pages first, then other pages
        return caption_pages + [p for p in pages_found if p not in caption_pages]
    
    def _extract_multiple_pages_png(self, pages: List[Tuple[fitz.Document, int]], ref: str = "unknown") -> Optional[str]:
        """Extract multiple pages as a combined PNG image."""
        if not pages:
            return None
            
        # Sort pages by document and page number
        pages.sort(key=lambda x: (id(x[0]), x[1]))
        
        # Extract the range of pages including one page after for tables
        all_images = []
        for i, (doc, page_num) in enumerate(pages):
            # Add the current page
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = doc.load_page(page_num).get_pixmap(matrix=mat)
            pix = self._ensure_rgb_pixmap(pix)
            all_images.append(pix)
            
            # Add the next page as well for tables (in case data continues)
            next_page_num = page_num + 1
            if next_page_num < doc.page_count:
                try:
                    next_pix = doc.load_page(next_page_num).get_pixmap(matrix=mat)
                    next_pix = self._ensure_rgb_pixmap(next_pix)
                    all_images.append(next_pix)
                    LOGGER.info("Including next page (%d) for table %s", next_page_num + 1, ref)
                except Exception as e:
                    LOGGER.warning("Failed to extract next page %d for %s: %s", next_page_num + 1, ref, e)
        
        if not all_images:
            return None
            
        # If only one page, return it directly
        if len(all_images) == 1:
            pix = self._ensure_rgb_pixmap(all_images[0])
            img_bytes = pix.tobytes("png")
            
            # Save debug file if available
            if self.debug_dir:
                timestamp = int(time.time())
                png_file = self.debug_dir / f"page_{ref.replace(' ', '_')}_{timestamp}.png"
                with open(png_file, 'wb') as f:
                    f.write(img_bytes)
                LOGGER.info("Saved multi-page image to: %s", png_file)
            
            return b64encode(img_bytes).decode()
            
        # Combine multiple pages vertically
        if not all_images:
            return None
            
        if len(all_images) == 1:
            pix = self._ensure_rgb_pixmap(all_images[0])
            return b64encode(pix.tobytes("png")).decode()
            
        # Calculate dimensions for combined image
        total_height = sum(pix.height for pix in all_images)
        max_width = max(pix.width for pix in all_images)
        
        LOGGER.info(f"Combining {len(all_images)} pages into single image ({max_width}x{total_height})")
        
        # Create a new document with a single page that can hold all images
        output_doc = fitz.open()
        
        # Create a page with the combined dimensions
        # Note: PDF pages have a max size, so we scale if needed
        max_pdf_dimension = 14400  # PDF max is ~200 inches at 72 DPI
        scale = 1.0
        if total_height > max_pdf_dimension or max_width > max_pdf_dimension:
            scale = min(max_pdf_dimension / total_height, max_pdf_dimension / max_width)
            total_height = int(total_height * scale)
            max_width = int(max_width * scale)
            LOGGER.warning(f"Scaling down by {scale:.2f} to fit PDF limits")
        
        page = output_doc.new_page(width=max_width, height=total_height)
        
        # Insert each image into the page
        y_offset = 0
        for i, pix in enumerate(all_images):
            # Center each image horizontally
            x_offset = (max_width - pix.width * scale) / 2
            
            # Create rect for image placement
            rect = fitz.Rect(x_offset, y_offset, 
                           x_offset + pix.width * scale, 
                           y_offset + pix.height * scale)
            
            # Insert the image
            page.insert_image(rect, pixmap=pix)
            y_offset += pix.height * scale
            
        # Convert the page to a pixmap
        # Limit zoom factor to avoid creating excessively large images
        # Gemini has limits on image size (approx 20MB or 20 megapixels)
        zoom = 5.0
        estimated_pixels = (max_width * zoom) * (total_height * zoom)
        max_pixels = 20_000_000  # 20 megapixels
        
        if estimated_pixels > max_pixels:
            # Calculate appropriate zoom to stay under limit
            zoom = min(5.0, (max_pixels / (max_width * total_height)) ** 0.5)
            LOGGER.warning(f"Reducing zoom from 5.0 to {zoom:.2f} to stay under {max_pixels/1e6:.1f} megapixel limit")
        
        mat = fitz.Matrix(zoom, zoom)
        combined_pix = page.get_pixmap(matrix=mat)
        combined_pix = self._ensure_rgb_pixmap(combined_pix)
        
        # Convert to PNG and return
        img_bytes = combined_pix.tobytes("png")
        
        # Check final size
        final_size_mb = len(img_bytes) / (1024 * 1024)
        if final_size_mb > 20:
            LOGGER.warning(f"Combined image is {final_size_mb:.1f}MB, may be too large for vision API")
        output_doc.close()
        
        # Save debug file if available
        if self.debug_dir:
            timestamp = int(time.time())
            png_file = self.debug_dir / f"combined_pages_{ref.replace(' ', '_')}_{timestamp}.png"
            with open(png_file, 'wb') as f:
                f.write(img_bytes)
            LOGGER.info("Saved combined multi-page image to: %s", png_file)
        
        return b64encode(img_bytes).decode()

    # ------------------------------------------------------------------
    # 6.3 Extract metrics in batch
    # ------------------------------------------------------------------
    
    def _validate_location_exists(self, ref: str) -> bool:
        """Verify that the referenced location actually exists in the document."""
        # Use the caption index to check if location exists
        result = self._page_with_reference(ref)
        return result is not None

    def _validate_context(self, snippet: str, enzyme_list: List[str], ref: str) -> bool:
        """Validate that the context contains meaningful content for extraction."""
        if not snippet or len(snippet.strip()) < 50:
            LOGGER.warning("Insufficient context for extraction from %s - skipping", ref)
            return False
        
        # Check if context actually mentions the enzymes we're looking for
        enzyme_mentions = sum(1 for enzyme in enzyme_list if enzyme.lower() in snippet.lower())
        if enzyme_mentions == 0:
            LOGGER.warning("No enzyme mentions found in context for %s - skipping", ref)
            return False
        
        # Check for performance-related keywords
        performance_keywords = ['yield', 'selectivity', 'conversion', 'ee', 'er', 'ttn', 'ton', 'tof', '%', 'percent']
        has_performance_data = any(keyword in snippet.lower() for keyword in performance_keywords)
        
        if not has_performance_data:
            LOGGER.warning("No performance metrics found in context for %s - skipping", ref)
            return False
        
        LOGGER.info("Context validated for %s: %d chars, %d enzyme mentions", ref, len(snippet), enzyme_mentions)
        return True

    def _validate_response(self, data: Union[Dict, List], enzyme_list: List[str], ref: str) -> bool:
        """Validate that the response contains meaningful data for the requested enzymes."""
        if not data:
            LOGGER.warning("Empty response from %s - skipping", ref)
            return False
        
        # Handle array format
        if isinstance(data, list):
            enzymes_with_data = 0
            for item in data:
                if isinstance(item, dict):
                    # Check if item has 'enzyme_name' field (standard format)
                    if 'enzyme_name' in item:
                        # Check if enzyme_name matches any in our list
                        enzyme_name = item['enzyme_name']
                        matched = any(
                            enzyme_name == enzyme or 
                            enzyme_name.startswith(enzyme) or 
                            enzyme in enzyme_name 
                            for enzyme in enzyme_list
                        )
                        
                        if matched:
                            # Check if there's at least one non-null metric
                            metrics = ['yield', 'ttn', 'ton', 'selectivity', 'conversion', 'tof', 'activity']
                            has_metric = any(item.get(metric) is not None for metric in metrics)
                            if has_metric:
                                enzymes_with_data += 1
                    else:
                        # Handle case where array item has enzyme name as key (e.g., {"ParPgb-HYA-5209": {...}})
                        for enzyme_key, metrics_data in item.items():
                            if isinstance(metrics_data, dict):
                                # Try to match the key against our enzyme list
                                matched = any(
                                    enzyme_key == enzyme or 
                                    enzyme_key.startswith(enzyme) or 
                                    enzyme in enzyme_key 
                                    for enzyme in enzyme_list
                                )
                                
                                if matched:
                                    # Check if there's at least one non-null metric
                                    metrics = ['yield', 'ttn', 'ton', 'selectivity', 'conversion', 'tof', 'activity']
                                    has_metric = any(metrics_data.get(metric) is not None for metric in metrics)
                                    if has_metric:
                                        enzymes_with_data += 1
            
            if enzymes_with_data == 0:
                LOGGER.warning("No valid metrics found in array response from %s - skipping", ref)
                return False
            
            LOGGER.info("Array response validated for %s: %d enzymes with data", ref, enzymes_with_data)
            return True
        
        # Handle dict format
        elif not isinstance(data, dict):
            LOGGER.warning("Invalid response format from %s - skipping", ref)
            return False
        
        # Check if we got data for at least one enzyme using flexible matching
        enzymes_with_data = 0
        for key, enzyme_data in data.items():
            # Check if this key contains any of our target enzymes
            matched = False
            for enzyme in enzyme_list:
                # Try multiple matching strategies
                if key == enzyme:  # Exact match
                    matched = True
                    break
                elif key.startswith(enzyme):  # Starts with
                    matched = True
                    break
                elif enzyme in key:  # Contains
                    matched = True
                    break
                else:
                    # Normalized comparison
                    normalized_key = key.replace(" ", "").replace("(", "").replace(")", "").lower()
                    normalized_enzyme = enzyme.replace(" ", "").replace("(", "").replace(")", "").lower()
                    if normalized_enzyme in normalized_key:
                        matched = True
                        break
            
            if matched:
                # Handle both dict and list formats
                if isinstance(enzyme_data, dict) and enzyme_data:
                    # Check if there's at least one non-null metric
                    metrics = ['yield', 'ttn', 'ton', 'selectivity', 'conversion', 'tof', 'activity']
                    has_metric = any(enzyme_data.get(metric) is not None for metric in metrics)
                    if has_metric:
                        enzymes_with_data += 1
                elif isinstance(enzyme_data, list) and enzyme_data:
                    # For list format, check if any item has metrics
                    metrics = ['yield', 'ttn', 'ton', 'selectivity', 'conversion', 'tof', 'activity']
                    for item in enzyme_data:
                        if isinstance(item, dict):
                            has_metric = any(item.get(metric) is not None for metric in metrics)
                            if has_metric:
                                enzymes_with_data += 1
                                break  # Count enzyme once even if multiple measurements
        
        if enzymes_with_data == 0:
            LOGGER.warning("No valid metrics found in response from %s - skipping", ref)
            return False
        
        LOGGER.info("Response validated for %s: %d enzymes with data", ref, enzymes_with_data)
        return True

    def extract_metrics_batch(self, enzyme_list: List[str], ref: Union[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract performance metrics for multiple enzymes from the identified location in batch.
        
        Args:
            enzyme_list: List of enzyme names to extract metrics for
            ref: Either a string reference (e.g., "Fig. 3") or a location dict with 'location' and optionally 'caption'
        """
        # Handle both string and dict inputs
        if isinstance(ref, dict):
            location_str = ref['location']
            caption_hint = ref.get('caption', '')
            document_hint = ref.get('document', '')
            LOGGER.info("extract_metrics_batch called with location='%s' (with caption hint, document=%s) for %d enzymes", 
                       location_str, document_hint, len(enzyme_list))
        else:
            location_str = ref
            caption_hint = ''
            document_hint = ''
            LOGGER.info("extract_metrics_batch called with ref='%s' for %d enzymes", location_str, len(enzyme_list))
        ref_lc = location_str.lower()
        image_b64: Optional[str] = None
        
        # Check document type and load appropriate PDF
        use_full_pdf = False
        pdf_data = None
        pdf_type = ""
        
        if document_hint:
            if document_hint.lower() == "manuscript":
                LOGGER.info("Performance data is in manuscript - will send full manuscript as PDF")
                pdf_type = "manuscript"
                try:
                    if hasattr(self, 'ms_pdf_path') and self.ms_pdf_path:
                        with open(self.ms_pdf_path, 'rb') as pdf_file:
                            pdf_data = pdf_file.read()
                        LOGGER.info("Successfully loaded manuscript PDF (%d bytes) for performance extraction", len(pdf_data))
                        use_full_pdf = True
                    else:
                        LOGGER.warning("No manuscript PDF path available")
                except Exception as e:
                    LOGGER.warning("Failed to load manuscript PDF: %s", e)
            elif document_hint.lower() in ["supplementary", "si"]:
                LOGGER.info("Performance data is in supplementary information - will send full SI as PDF")
                pdf_type = "supplementary"
                try:
                    if hasattr(self, 'si_pdf_path') and self.si_pdf_path:
                        with open(self.si_pdf_path, 'rb') as pdf_file:
                            pdf_data = pdf_file.read()
                        LOGGER.info("Successfully loaded SI PDF (%d bytes) for performance extraction", len(pdf_data))
                        use_full_pdf = True
                    else:
                        LOGGER.warning("No SI PDF path available")
                except Exception as e:
                    LOGGER.warning("Failed to load SI PDF: %s", e)
        
        # Skip validation entirely when we have a caption hint - trust the vision model
        if caption_hint:
            LOGGER.info("Skipping validation - using caption hint for %s", location_str)
        else:
            # Try fuzzy matching instead of strict validation
            # Don't skip locations - attempt extraction anyway
            if not self._validate_location_exists(location_str):
                LOGGER.warning("Location %s not found with exact match - attempting fuzzy extraction", location_str)
        
        # Add campaign context if available
        campaign_context = ""
        if self.campaign_filter:
            campaign_context = f"\n\nIMPORTANT: You are extracting data for the {self.campaign_filter} campaign.\nOnly extract data that is relevant to this specific campaign.\nEXCLUDE reference variants from other publications - only include variants created/tested in THIS study.\n"
        
        # If using full PDF, skip normal extraction
        snippet = ""
        if not use_full_pdf:
            if self._TAB_RE.search(ref_lc):
                # For tables, try to extract the page as an image first
                image_b64 = self._extract_page_png(location_str, extract_figure_only=False, document_hint=document_hint)
                if not image_b64:
                    LOGGER.debug("No page image found for %s - using full page text", location_str)
                    snippet = self._extract_table_context(location_str)
            elif self._FIG_RE.search(ref_lc):
                # For figures, extract just the figure image (same logic as compound mapping)
                LOGGER.info("Attempting to extract figure image for '%s'", location_str)
                image_b64 = self._extract_page_png(location_str, extract_figure_only=True, caption_hint=caption_hint, document_hint=document_hint)
                if not image_b64:
                    LOGGER.warning("Failed to extract figure image for '%s' - falling back to caption text", location_str)
                    snippet = self._extract_figure_caption(location_str)
                    LOGGER.debug("Caption extraction result: %s", 
                               f"'{snippet[:100]}...'" if snippet else "empty")
                else:
                    LOGGER.info("Successfully extracted figure image for '%s'", location_str)
                    # If figure is found, ignore text information - use image only
                    snippet = ""
            else:
                snippet = self._page_with_reference(location_str) or ""

        # For figures with images, skip text validation and proceed with image extraction
        if (image_b64 and self._FIG_RE.search(ref_lc)) or use_full_pdf:
            LOGGER.info("Using %s for %s - ignoring text context", 
                        f"full {pdf_type} PDF" if use_full_pdf else "figure image", 
                        location_str)
        elif not image_b64 and not use_full_pdf and not self._validate_context(snippet, enzyme_list, location_str):
            return []

        # Create enhanced enzyme descriptions with parent/mutation context
        if hasattr(self, 'enzyme_df') and self.enzyme_df is not None:
            enzyme_descriptions = []
            for enzyme in enzyme_list:
                # Find this enzyme in the dataframe
                enzyme_row = None
                if 'enzyme_id' in self.enzyme_df.columns:
                    enzyme_row = self.enzyme_df[self.enzyme_df['enzyme_id'] == enzyme]
                elif 'enzyme' in self.enzyme_df.columns:
                    enzyme_row = self.enzyme_df[self.enzyme_df['enzyme'] == enzyme]
                
                if enzyme_row is not None and len(enzyme_row) > 0:
                    row = enzyme_row.iloc[0]
                    parent = row.get('parent_enzyme_id', '')
                    mutations = row.get('mutations', '')
                    
                    desc = f"- {enzyme}"
                    if parent and str(parent).strip() and str(parent) != 'nan':
                        desc += f" (parent: {parent})"
                    if mutations and str(mutations).strip() and str(mutations) != 'nan':
                        desc += f" (mutations: {mutations})"
                    enzyme_descriptions.append(desc)
                else:
                    enzyme_descriptions.append(f"- {enzyme}")
            enzyme_names = "\n".join(enzyme_descriptions)
        else:
            enzyme_names = "\n".join([f"- {enzyme}" for enzyme in enzyme_list])
        
        if image_b64 or pdf_data:
            # Use batch extraction prompt for image/PDF analysis
            if pdf_data:
                location_context = f"\n\nIMPORTANT: The performance data is primarily located at {location_str} in the {pdf_type.upper()}."
                
                # Add all other locations if available
                all_locations = ref.get('all_locations', []) if isinstance(ref, dict) else []
                if len(all_locations) > 1:
                    other_locations = [loc['location'] for loc in all_locations[1:]]  # Skip first as it's the primary
                    location_context += f"\n\nAdditional data may also be found at: {', '.join(other_locations)}"
                    LOGGER.info("Providing %d total locations to Gemini for comprehensive extraction", len(all_locations))
                
                location_context += f"\n\nThe attached PDF contains the complete {pdf_type}. Please check ALL these locations to extract comprehensive performance data.\n"
                LOGGER.info("Gemini Vision: extracting metrics for %d enzymes from FULL %s PDF (primary location: %s)…", len(enzyme_list), pdf_type.upper(), location_str)
                tag = f"extract_metrics_batch_full_{pdf_type}_pdf"
            else:
                location_context = f"\n\nIMPORTANT: You are extracting data from {ref}, which has been identified as the PRIMARY LOCATION containing the most reliable performance data for these enzymes.\n"
                LOGGER.info("Gemini Vision: extracting metrics for %d enzymes from %s…", len(enzyme_list), ref)
                tag = f"extract_metrics_batch_vision"
            
            prompt = campaign_context + location_context + PROMPT_EXTRACT_FIGURE_METRICS_BATCH.format(enzyme_names=enzyme_names)
            
            # Save the figure image to debug directory
            if self.debug_dir and isinstance(ref, dict):
                location_str = ref.get('location', str(ref))
            else:
                location_str = str(ref)
            
            if self.debug_dir:
                timestamp = int(time.time())
                img_file = self.debug_dir / f"metrics_extraction_{location_str.replace(' ', '_').replace('.', '')}_{timestamp}.png"
                try:
                    import base64
                    img_bytes = base64.b64decode(image_b64)
                    with open(img_file, 'wb') as f:
                        f.write(img_bytes)
                    LOGGER.info("Saved metrics extraction figure to: %s", img_file)
                except Exception as e:
                    LOGGER.warning("Failed to save metrics extraction figure: %s", e)
        else:
            # Add enzyme names to prompt for batch extraction with explicit format requirement
            format_example = '{"enzyme1": {"yield": "99.0%", "ttn": null, ...}, "enzyme2": {"yield": "85.0%", ...}}'
            prompt = campaign_context + PROMPT_EXTRACT_METRICS + f"\n\nExtract performance data for ALL these enzyme variants:\n{enzyme_names}\n\nReturn a JSON object with enzyme names as keys, each containing the metrics.\nExample format: {format_example}\n\n=== CONTEXT ===\n" + snippet[:4000]
            LOGGER.info("Gemini: extracting metrics for %d enzymes from %s…", len(enzyme_list), ref)
            tag = f"extract_metrics_batch"

        try:
            # Handle full PDF separately
            if pdf_data:
                # Prepare multimodal content with PDF
                content_parts = [
                    prompt,
                    {
                        "mime_type": "application/pdf",
                        "data": pdf_data
                    }
                ]
                
                # Configure model and make API call
                model = genai.GenerativeModel(
                    model_name=self.cfg.model_name,
                    generation_config={
                        "temperature": self.cfg.extract_temperature,
                        "top_p": self.cfg.top_p,
                        "max_output_tokens": self.cfg.max_tokens,
                    }
                )
                
                LOGGER.info("Sending %s PDF to Gemini for performance extraction", pdf_type)
                response = model.generate_content(content_parts)
                
                if response and response.text:
                    # Save debug output
                    if self.debug_dir:
                        timestamp = int(time.time())
                        _dump(prompt, self.debug_dir / f"metrics_extraction_{pdf_type}_pdf_prompt_{timestamp}.txt")
                        _dump(response.text, self.debug_dir / f"metrics_extraction_{pdf_type}_pdf_response_{timestamp}.txt")
                    
                    # Extract JSON from response
                    text = response.text.strip()
                    if text.startswith("```json"):
                        text = text[7:]
                    if text.endswith("```"):
                        text = text[:-3]
                    data = json.loads(text.strip())
                else:
                    data = {}
            else:
                # Use normal single-image extraction
                data = generate_json_with_retry(
                    self.model,
                    prompt,
                    temperature=self.cfg.extract_temperature,
                    debug_dir=self.debug_dir,
                    tag=tag,
                    image_b64=image_b64
                )
            
            # Log the type and content of data for debugging
            LOGGER.info("Received data type: %s", type(data))
            if isinstance(data, list):
                LOGGER.info("Data is array with %d items", len(data))
                if data and len(data) > 0:
                    LOGGER.info("First item keys: %s", list(data[0].keys()) if isinstance(data[0], dict) else "Not a dict")
            elif isinstance(data, dict):
                LOGGER.info("Data is dict with keys: %s", list(data.keys()))
            else:
                LOGGER.warning("Unexpected data type: %s", type(data))
            
            # Validate response has meaningful data
            if not self._validate_response(data, enzyme_list, ref):
                # If figure extraction failed and we have a figure, try falling back to text
                if image_b64 and self._FIG_RE.search(ref_lc):
                    LOGGER.warning("Figure extraction from %s returned empty results - falling back to text", ref)
                    snippet = self._extract_figure_caption(ref)
                    if self._validate_context(snippet, enzyme_list, ref):
                        # Retry with text extraction
                        format_example = '{"enzyme1": {"yield": "99.0%", "ttn": null, ...}, "enzyme2": {"yield": "85.0%", ...}}'
                        prompt = campaign_context + PROMPT_EXTRACT_METRICS + f"\n\nExtract performance data for ALL these enzyme variants:\n{enzyme_names}\n\nReturn a JSON object with enzyme names as keys, each containing the metrics.\nExample format: {format_example}\n\n=== CONTEXT ===\n" + snippet[:4000]
                        LOGGER.info("Gemini: retrying with text extraction for %d enzymes from %s…", len(enzyme_list), ref)
                        
                        data = generate_json_with_retry(
                            self.model,
                            prompt,
                            temperature=self.cfg.extract_temperature,
                            debug_dir=self.debug_dir,
                            tag=f"extract_metrics_batch_text_fallback",
                            image_b64=None
                        )
                        
                        # Validate the text extraction response
                        if not self._validate_response(data, enzyme_list, ref):
                            return []
                    else:
                        return []
                else:
                    return []
            
            # Handle the response format - can be either dict with enzyme names as keys or array of objects
            results = []
            if isinstance(data, list):
                # Handle array format
                LOGGER.info("Response is an array with %d entries", len(data))
                for item in data:
                    if isinstance(item, dict):
                        # Check if item has 'enzyme_name' field (standard format)
                        if 'enzyme_name' in item:
                            # Extract the enzyme name and match it to our list
                            enzyme_name = item['enzyme_name']
                            matched_enzyme = None
                            
                            # Try to match against our enzyme list
                            for enzyme in enzyme_list:
                                if enzyme_name == enzyme or enzyme_name.startswith(enzyme) or enzyme in enzyme_name:
                                    matched_enzyme = enzyme
                                    break
                            
                            if matched_enzyme:
                                # Create result entry with standardized fields
                                result_entry = {
                                    "enzyme": matched_enzyme,
                                    "location_ref": ref,
                                    "used_image": bool(image_b64)
                                }
                                
                                # Copy over all the metrics
                                for key, value in item.items():
                                    if key != 'enzyme_name':
                                        result_entry[key] = value
                                
                                results.append(result_entry)
                                LOGGER.debug("Matched array entry '%s' to enzyme '%s'", enzyme_name, matched_enzyme)
                            else:
                                LOGGER.warning("Could not match array entry '%s' to any enzyme in list", enzyme_name)
                        else:
                            # Handle case where array item has enzyme name as key (e.g., {"ParPgb-HYA-5209": {...}})
                            # This is the format we're seeing in the debug file
                            for enzyme_key, metrics_data in item.items():
                                if isinstance(metrics_data, dict):
                                    # Try to match the key against our enzyme list
                                    matched_enzyme = None
                                    for enzyme in enzyme_list:
                                        if enzyme_key == enzyme or enzyme_key.startswith(enzyme) or enzyme in enzyme_key:
                                            matched_enzyme = enzyme
                                            break
                                    
                                    if matched_enzyme:
                                        # Create result entry with standardized fields
                                        result_entry = {
                                            "enzyme": matched_enzyme,
                                            "location_ref": ref,
                                            "used_image": bool(image_b64)
                                        }
                                        
                                        # Copy over all the metrics from the nested dict
                                        for key, value in metrics_data.items():
                                            result_entry[key] = value
                                        
                                        results.append(result_entry)
                                        LOGGER.debug("Matched array entry with key '%s' to enzyme '%s'", enzyme_key, matched_enzyme)
                                    else:
                                        LOGGER.warning("Could not match array entry with key '%s' to any enzyme in list", enzyme_key)
                
            elif isinstance(data, dict):
                LOGGER.info("Response contains %d entries", len(data))
                LOGGER.debug("Response keys: %s", list(data.keys()))
                
                # First, collect all entries that match our enzyme list
                for key, enzyme_data in data.items():
                    # Check if this key contains any of our target enzymes
                    matched_enzyme = None
                    best_match_score = 0
                    
                    for enzyme in enzyme_list:
                        # Try multiple matching strategies
                        # 1. Exact match
                        if key == enzyme:
                            matched_enzyme = enzyme
                            break
                        
                        # 2. Key starts with enzyme name
                        if key.startswith(enzyme):
                            matched_enzyme = enzyme
                            best_match_score = 0.9
                        
                        # 3. Enzyme name is in key (but not at start)
                        elif enzyme in key and best_match_score < 0.8:
                            matched_enzyme = enzyme
                            best_match_score = 0.8
                        
                        # 4. Normalized comparison (remove spaces, parentheses, etc.)
                        elif best_match_score < 0.7:
                            normalized_key = key.replace(" ", "").replace("(", "").replace(")", "").lower()
                            normalized_enzyme = enzyme.replace(" ", "").replace("(", "").replace(")", "").lower()
                            if normalized_enzyme in normalized_key:
                                matched_enzyme = enzyme
                                best_match_score = 0.7
                    
                    if matched_enzyme:
                        # Handle both dict and list formats
                        if isinstance(enzyme_data, dict):
                            LOGGER.debug("Matched key '%s' to enzyme '%s'", key, matched_enzyme)
                            
                            # Normalize keys
                            if "TTN" in enzyme_data and "ttn" not in enzyme_data:
                                enzyme_data["ttn"] = enzyme_data.pop("TTN")
                            
                            # Add metadata
                            enzyme_data["enzyme"] = matched_enzyme  # Use the exact name from enzyme_list
                            enzyme_data["location_ref"] = ref
                            enzyme_data["used_image"] = bool(image_b64)
                            
                            # Keep the original key info if it had condition information
                            if key != matched_enzyme and "catalyst_form" not in enzyme_data:
                                LOGGER.debug("Key '%s' might contain condition info beyond enzyme name '%s'", key, matched_enzyme)
                            
                            results.append(enzyme_data)
                        elif isinstance(enzyme_data, list):
                            LOGGER.debug("Matched key '%s' to enzyme '%s' (list with %d entries)", key, matched_enzyme, len(enzyme_data))
                            
                            # Process each entry in the list
                            for entry in enzyme_data:
                                if isinstance(entry, dict):
                                    # Create a copy to avoid modifying original
                                    entry_copy = entry.copy()
                                    
                                    # Normalize keys
                                    if "TTN" in entry_copy and "ttn" not in entry_copy:
                                        entry_copy["ttn"] = entry_copy.pop("TTN")
                                    
                                    # Add metadata
                                    entry_copy["enzyme"] = matched_enzyme
                                    entry_copy["location_ref"] = ref
                                    entry_copy["used_image"] = bool(image_b64)
                                    
                                    results.append(entry_copy)
                
                # Check if we missed any enzymes
                found_enzymes = {r["enzyme"] for r in results}
                for enzyme in enzyme_list:
                    if enzyme not in found_enzymes:
                        LOGGER.warning("No data found for enzyme: %s", enzyme)
            else:
                # Fallback if response format is unexpected
                LOGGER.warning("Unexpected response format from batch extraction")
                for enzyme in enzyme_list:
                    results.append({
                        "enzyme": enzyme,
                        "location_ref": ref,
                        "used_image": bool(image_b64),
                        "error": "Invalid response format"
                    })
                    
        except Exception as e:
            LOGGER.warning("Failed to extract metrics batch: %s", e)
            results = []
            for enzyme in enzyme_list:
                results.append({
                    "enzyme": enzyme,
                    "location_ref": ref,
                    "used_image": bool(image_b64),
                    "error": str(e)
                })
        
        return results

    # Removed extract_iupac_names - substrate scope IUPAC extraction no longer needed

    # ------------------------------------------------------------------
    # 6.4 Model reaction with location finding
    # ------------------------------------------------------------------

    def find_model_reaction_locations(self, enzyme_variants: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Find locations for model reaction scheme, conditions, and IUPAC names."""
        # Create cache key based on campaign filter and enzyme variants
        cache_key = f"{self.campaign_filter}_{hash(tuple(sorted(enzyme_variants)) if enzyme_variants else ())}"
        
        # Check cache first
        cached_result = self._model_reaction_locations_cache.get(cache_key)
        if cached_result is not None:
            LOGGER.info("Using cached model reaction locations for campaign: %s", self.campaign_filter)
            return cached_result
        
        # Add enzyme context if provided
        enzyme_context = ""
        if enzyme_variants and self.campaign_filter:
            campaigns_context = ""
            if self.all_campaigns:
                campaigns_context = f"""
ALL CAMPAIGNS IN THIS PAPER:
{chr(10).join([f"- {campaign}" for campaign in self.all_campaigns])}

CRITICAL WARNING: Do NOT confuse campaigns! Each campaign uses completely different substrates:
- Different campaigns may use similar enzyme names but different substrates
- Be extremely careful to only extract data for the {self.campaign_filter} campaign
- Ignore data from other campaigns even if they seem similar
"""
            
            enzyme_context = f"""
IMPORTANT CONTEXT:
You are looking for the model reaction used specifically for these enzyme variants:
{', '.join(enzyme_variants[:10])}{'...' if len(enzyme_variants) > 10 else ''}

These variants belong to campaign: {self.campaign_filter}
{campaigns_context}
Focus on finding the model reaction that was used to evaluate THESE specific variants.
Different campaigns may use different model reactions.

CRITICAL: These variants should be from THIS study only!
- EXCLUDE any reference variants cited from other publications
- Only include variants that were created/engineered in this manuscript
"""
        
        # Update prompt to indicate PDFs are attached
        prompt = enzyme_context + PROMPT_FIND_MODEL_REACTION_LOCATION + "\n\n=== FULL PDFs ATTACHED ===\nI've attached both the manuscript and supplementary information PDFs for you to analyze. Please search through these documents to find the model reaction scheme, conditions, and IUPAC names."
        
        # Build multimodal prompt with both PDFs
        content_parts = [prompt]
        
        # Add manuscript PDF
        if self.ms_pdf_path:
            try:
                with open(self.ms_pdf_path, 'rb') as f:
                    ms_pdf_data = f.read()
                content_parts.append({
                    "mime_type": "application/pdf",
                    "data": ms_pdf_data
                })
                LOGGER.info("Added manuscript PDF to multimodal prompt for model reaction location")
            except Exception as e:
                LOGGER.error("Failed to load manuscript PDF: %s", e)
        
        # Add SI PDF
        if self.si_pdf_path:
            try:
                with open(self.si_pdf_path, 'rb') as f:
                    si_pdf_data = f.read()
                content_parts.append({
                    "mime_type": "application/pdf",
                    "data": si_pdf_data
                })
                LOGGER.info("Added SI PDF to multimodal prompt for model reaction location")
            except Exception as e:
                LOGGER.error("Failed to load SI PDF: %s", e)
        
        try:
            # Use multimodal API call directly
            model = genai.GenerativeModel(
                self.cfg.model_name,
                generation_config={
                    "temperature": self.cfg.location_temperature,
                    "max_output_tokens": self.cfg.max_tokens,
                }
            )
            
            response = model.generate_content(content_parts)
            
            if response and response.text:
                # Save debug output
                if self.debug_dir:
                    timestamp = int(time.time())
                    debug_file = self.debug_dir / f"find_model_reaction_locations_response_{timestamp}.txt"
                    with open(debug_file, 'w') as f:
                        f.write("="*80 + "\n")
                        f.write("=== RESPONSE FOR FIND_MODEL_REACTION_LOCATIONS ===\n")
                        f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Length: {len(response.text)} characters\n")
                        f.write(f"Hash: {hashlib.sha256(response.text.encode()).hexdigest()}\n")
                        f.write("="*80 + "\n\n")
                        f.write(response.text)
                    LOGGER.info("Debug response saved to: %s", debug_file)
                
                # Parse response
                try:
                    if response.text.strip().startswith('```json'):
                        json_str = response.text.strip()[7:-3]
                    else:
                        json_str = response.text.strip()
                    data = json.loads(json_str)
                    
                    # Cache the result
                    self._model_reaction_locations_cache.put(cache_key, data)
                    LOGGER.info("Cached model reaction locations for campaign: %s", self.campaign_filter)
                    
                    return data
                except json.JSONDecodeError as e:
                    LOGGER.error("Failed to parse JSON response: %s", e)
                    LOGGER.error("Response text: %s", response.text[:500])
                    return None
            else:
                LOGGER.error("Empty response from model")
                return None
                
        except Exception as e:
            LOGGER.error("Failed to find model reaction locations: %s", e)
            return None

    def _get_text_around_location(self, location: str) -> Optional[str]:
        """Extract text around a given location identifier."""
        location_lower = location.lower()
        
        # Handle compound locations like "Figure 2 caption and Section I"
        # Extract the first figure/table/scheme reference
        figure_match = re.search(r"(figure|scheme|table)\s*\d+", location_lower)
        if figure_match:
            primary_location = figure_match.group(0)
            # Try to find this primary location first
            for page_text in self.all_pages:
                if primary_location in page_text.lower():
                    idx = page_text.lower().index(primary_location)
                    start = max(0, idx - 500)
                    end = min(len(page_text), idx + 3000)
                    return page_text[start:end]
        
        # Search in all pages for exact match
        for page_text in self.all_pages:
            if location_lower in page_text.lower():
                # Find the location and extract context around it
                idx = page_text.lower().index(location_lower)
                start = max(0, idx - 500)
                end = min(len(page_text), idx + 3000)
                return page_text[start:end]
        
        # If not found in exact form, try pattern matching
        # For scheme/figure references
        if re.search(r"(scheme|figure|table)\s*\d+", location_lower):
            pattern = re.compile(location.replace(" ", r"\s*"), re.I)
            for page_text in self.all_pages:
                match = pattern.search(page_text)
                if match:
                    start = max(0, match.start() - 500)
                    end = min(len(page_text), match.end() + 3000)
                    return page_text[start:end]
        
        return None

    def _get_extended_text_around_location(self, location: str, before: int = 2000, after: int = 10000) -> Optional[str]:
        """Extract extended text around a given location identifier."""
        location_lower = location.lower()
        
        # Search in all pages
        for i, page_text in enumerate(self.all_pages):
            if location_lower in page_text.lower():
                # Find the location
                idx = page_text.lower().index(location_lower)
                
                # Collect text from multiple pages if needed
                result = []
                
                # Start from current page
                start = max(0, idx - before)
                result.append(page_text[start:])
                
                # Add subsequent pages up to 'after' characters
                chars_collected = len(page_text) - start
                page_idx = i + 1
                
                while chars_collected < after + before and page_idx < len(self.all_pages):
                    next_page = self.all_pages[page_idx]
                    chars_to_take = min(len(next_page), after + before - chars_collected)
                    result.append(next_page[:chars_to_take])
                    chars_collected += chars_to_take
                    page_idx += 1
                
                return "\n".join(result)
        
        return None

    def _extract_sections_by_title(self, sections: List[str], max_chars_per_section: int = 5000) -> str:
        """Extract text from sections with specific titles."""
        extracted_text = []
        
        for section_title in sections:
            pattern = re.compile(rf"{re.escape(section_title)}.*?(?=\n\n[A-Z]|\Z)", re.I | re.S)
            
            # Search in all pages
            for page in self.all_pages:
                match = pattern.search(page)
                if match:
                    section_text = match.group(0)[:max_chars_per_section]
                    extracted_text.append(f"=== {section_title} ===\n{section_text}")
                    break
        
        return "\n\n".join(extracted_text)

    def _extract_compound_mappings_from_text(
        self,
        extraction_text: str,
        compound_ids: List[str] = None,
        tag_suffix: str = "",
        campaign_filter: Optional[str] = None,
    ) -> Dict[str, CompoundMapping]:
        """Helper function to extract compound mappings from provided text."""
        prompt = PROMPT_COMPOUND_MAPPING
        if campaign_filter:
            prompt += f"\n\nIMPORTANT: Focus on compound information relevant to the {campaign_filter} campaign/reaction system."
        
        # Add campaign info as hints
        if self.campaign_info:
            substrate_id = self.campaign_info.get('substrate_id', '')
            product_id = self.campaign_info.get('product_id', '')
            model_substrate = self.campaign_info.get('model_substrate', '')
            model_product = self.campaign_info.get('model_product', '')
            
            if substrate_id and model_substrate:
                prompt += f"\n\nHINT: The model substrate for this campaign is likely '{model_substrate}' (ID: {substrate_id})"
            if product_id and model_product:
                prompt += f"\nHINT: The model product for this campaign is likely '{model_product}' (ID: {product_id})"
        
        if compound_ids:
            prompt += "\n\nCOMPOUNDS TO MAP: " + ", ".join(sorted(compound_ids))
        prompt += "\n\nTEXT:\n" + extraction_text
        
        tag = f"compound_mapping_{tag_suffix}" if tag_suffix else "compound_mapping"
        
        try:
            data = generate_json_with_retry(
                self.model,
                prompt,
                temperature=self.cfg.model_reaction_temperature,
                debug_dir=self.debug_dir,
                tag=tag,
            )
            
            mappings = {}
            for item in data.get("compound_mappings", []):
                # Handle both old format (with identifiers list) and new format (with identifier string)
                identifiers = item.get("identifiers", [])
                if not identifiers and item.get("identifier"):
                    identifiers = [item.get("identifier")]
                
                mapping = CompoundMapping(
                    identifiers=identifiers,
                    iupac_name=item.get("iupac_name", ""),
                    common_names=item.get("common_names", []),
                    compound_type=item.get("compound_type", "unknown"),
                    source_location=item.get("source_location")
                )
                
                # Create lookup entries for all identifiers and common names
                for identifier in mapping.identifiers + mapping.common_names:
                    if identifier:
                        mappings[identifier.lower().strip()] = mapping
            
            return mappings
            
        except Exception as exc:
            LOGGER.error("Failed to extract compound mappings: %s", exc)
            return {}

    def _extract_compound_mappings_with_figures(
        self,
        text: str,
        compound_ids: List[str],
        figure_images: Dict[str, str],
        tag_suffix: str = "",
        campaign_filter: Optional[str] = None,
    ) -> Dict[str, CompoundMapping]:
        """Extract compound mappings using multimodal approach with figures."""
        # Enhanced prompt for figure-based extraction
        prompt = """You are analyzing chemical figures and manuscript text to identify compound IUPAC names.

TASK: Find the IUPAC names for these specific compound identifiers: """ + ", ".join(sorted(compound_ids)) + """

Use your best knowledge, Look carefully in:
1. The chemical structures shown in figures - infer IUPAC names from drawn structures
2. Figure captions that may define compounds
3. Text that refers to these compound numbers
4. Reaction schemes showing transformations"""

        if campaign_filter:
            campaigns_warning = ""
            if self.all_campaigns:
                campaigns_warning = f"""
ALL CAMPAIGNS IN THIS PAPER:
{chr(10).join([f"- {campaign}" for campaign in self.all_campaigns])}

CRITICAL WARNING: Do NOT confuse campaigns! Each campaign uses completely different substrates.
"""
            
            prompt += f"""

IMPORTANT CAMPAIGN CONTEXT: Focus on compound information relevant to the {campaign_filter} campaign/reaction system.
{campaigns_warning}
Different campaigns may use different numbering systems for compounds.
Do NOT include compound information from other campaigns."""
        
        # Add campaign info as hints
        if self.campaign_info:
            substrate_id = self.campaign_info.get('substrate_id', '')
            product_id = self.campaign_info.get('product_id', '')
            model_substrate = self.campaign_info.get('model_substrate', '')
            model_product = self.campaign_info.get('model_product', '')
            
            hints = []
            if substrate_id and model_substrate:
                hints.append(f"The model substrate for this campaign is likely '{model_substrate}' (ID: {substrate_id})")
            if product_id and model_product:
                hints.append(f"The model product for this campaign is likely '{model_product}' (ID: {product_id})")
            
            if hints:
                prompt += "\n\nHINTS FROM CAMPAIGN INFO:\n" + "\n".join(hints)

        prompt += """

IMPORTANT:
- Only provide IUPAC names you can determine from the figures or text
- If a structure is clearly shown in a figure, derive the IUPAC name from it

Return as JSON:
{
  "compound_mappings": [
    {
      "identifier": "compound identifier", 
      "iupac_name": "IUPAC name",
      "common_names": ["common names if any"],
      "compound_type": "substrate/product/reagent",
      "source_location": "where found (e.g., Figure 3, manuscript text)"
    }
  ]
}

TEXT FROM MANUSCRIPT:
""" + text
        
        # Prepare multimodal content
        content_parts = [prompt]
        
        # Add figure images
        if figure_images:
            for fig_ref, fig_base64 in figure_images.items():
                try:
                    img_bytes = b64decode(fig_base64)
                    # Format image for Gemini API
                    image_part = {"mime_type": "image/png", "data": img_bytes}
                    content_parts.append(f"\n[Figure: {fig_ref}]")
                    content_parts.append(image_part)
                    LOGGER.info("Added figure %s to multimodal compound mapping", fig_ref)
                except Exception as e:
                    LOGGER.warning("Failed to add figure %s: %s", fig_ref, e)
        
        tag = f"compound_mapping_{tag_suffix}" if tag_suffix else "compound_mapping"
        
        try:
            # Log multimodal call
            LOGGER.info("=== GEMINI MULTIMODAL API CALL: COMPOUND_MAPPING_WITH_FIGURES ===")
            LOGGER.info("Text prompt length: %d characters", len(prompt))
            LOGGER.info("Number of images: %d", len(content_parts) - 1)
            LOGGER.info("Compounds to find: %s", ", ".join(sorted(compound_ids)))
            
            # Save debug info
            if self.debug_dir:
                prompt_file = self.debug_dir / f"{tag}_prompt_{int(time.time())}.txt"
                with open(prompt_file, 'w') as f:
                    f.write(f"=== PROMPT FOR {tag.upper()} ===\n")
                    f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Text length: {len(prompt)} characters\n")
                    f.write(f"Images included: {len(content_parts) - 1}\n")
                    for fig_ref in figure_images.keys():
                        f.write(f"  - {fig_ref}\n")
                    f.write("="*80 + "\n\n")
                    f.write(prompt)
                LOGGER.info("Full prompt saved to: %s", prompt_file)
            
            # Make multimodal API call with increased token limit
            response = self.model.generate_content(
                content_parts,
                generation_config={
                    "temperature": 0.0,
                    "max_output_tokens": 32000,  # Increased for compound mapping
                }
            )
            
            # Track token usage if available
            try:
                if hasattr(response, 'usage_metadata'):
                    input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
                    output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)
                    if input_tokens or output_tokens:
                        try:
                            from .wrapper import add_token_usage
                            add_token_usage('reaction_info_extractor', input_tokens, output_tokens)
                        except ImportError:
                            pass  # wrapper not available
            except Exception:
                pass  # token tracking is best-effort
            
            raw_text = response.text.strip()
            
            # Log response
            LOGGER.info("Gemini multimodal response length: %d characters", len(raw_text))
            
            if self.debug_dir:
                response_file = self.debug_dir / f"{tag}_response_{int(time.time())}.txt"
                with open(response_file, 'w') as f:
                    f.write(f"=== RESPONSE FOR {tag.upper()} ===\n")
                    f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Length: {len(raw_text)} characters\n")
                    f.write("="*80 + "\n\n")
                    f.write(raw_text)
                LOGGER.info("Full response saved to: %s", response_file)
            
            # Parse JSON
            data = json.loads(raw_text.strip('```json').strip('```').strip())
            
            mappings = {}
            for item in data.get("compound_mappings", []):
                identifiers = item.get("identifiers", [])
                if not identifiers and item.get("identifier"):
                    identifiers = [item.get("identifier")]
                
                mapping = CompoundMapping(
                    identifiers=identifiers,
                    iupac_name=item.get("iupac_name", ""),
                    common_names=item.get("common_names", []),
                    compound_type=item.get("compound_type", "unknown"),
                    source_location=item.get("source_location")
                )
                
                for identifier in mapping.identifiers + mapping.common_names:
                    if identifier:
                        mappings[identifier.lower().strip()] = mapping
            
            return mappings
            
        except Exception as exc:
            LOGGER.error("Failed to extract compound mappings with figures: %s", exc)
            return {}

    def _extract_compound_mappings_adaptive(
        self,
        compound_ids: List[str],
        initial_sections: List[str] = None,
        campaign_filter: Optional[str] = None,
        iupac_location_hint: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, CompoundMapping]:
        """Extract compound ID to IUPAC name mappings using simplified 2-tier strategy.
        
        1. First attempts extraction from specific SI sections + 10 manuscript pages
        2. If compounds missing, uses full manuscript + SI with multimodal figure analysis
        """
        if not compound_ids:
            return {}
            
        # Check cache first - return cached results for compounds we've already processed
        cached_mappings = {}
        uncached_compound_ids = []
        
        for cid in compound_ids:
            # Include campaign filter in cache key to prevent cross-campaign contamination
            cache_key = f"{campaign_filter}_{cid.lower().strip()}" if campaign_filter else cid.lower().strip()
            cached_mapping = self._compound_mapping_cache.get(cache_key)
            if cached_mapping is not None:
                cached_mappings[cid.lower().strip()] = cached_mapping
                LOGGER.info("Using cached compound mapping for: %s (campaign: %s)", cid, campaign_filter)
            else:
                uncached_compound_ids.append(cid)
        
        # If all compounds are cached, return immediately
        if not uncached_compound_ids:
            LOGGER.info("All %d compounds found in cache, skipping API calls", len(compound_ids))
            return cached_mappings
            
        LOGGER.info("Starting adaptive compound mapping for %d uncached compounds: %s", 
                   len(uncached_compound_ids), sorted(uncached_compound_ids))
        
        # Tier 1: Use IUPAC location hint if provided, otherwise standard sections
        if iupac_location_hint and iupac_location_hint.get('location'):
            iupac_loc = iupac_location_hint.get('location')
            # Handle case where location is a list
            iupac_locations = iupac_loc if isinstance(iupac_loc, list) else [iupac_loc]
            LOGGER.info("Tier 1: Using IUPAC location hint: %s", iupac_locations)
            if iupac_location_hint.get('compound_section_hint'):
                LOGGER.info("Tier 1: Compound section hint: %s", iupac_location_hint.get('compound_section_hint'))
            
            # Extract text from the specific IUPAC location(s)
            iupac_text = ""
            for loc in iupac_locations:
                loc_text = self._get_extended_text_around_location(
                    loc, 
                    before=2000, 
                    after=10000
                )
                if loc_text:
                    iupac_text += f"\n\n=== {loc} ===\n{loc_text}"
            
            # Also check for compound-specific hints
            compound_hint = iupac_location_hint.get('compound_section_hint', '')
            if compound_hint and iupac_text:
                # Search for the specific compound section
                hint_pattern = re.escape(compound_hint)
                match = re.search(hint_pattern, iupac_text, re.IGNORECASE)
                if match:
                    # Extract more focused text around the compound hint
                    start = max(0, match.start() - 500)
                    end = min(len(iupac_text), match.end() + 2000)
                    iupac_text = iupac_text[start:end]
                    LOGGER.info("Found compound hint '%s' in IUPAC section", compound_hint)
            
            extraction_text = iupac_text or ""
            if extraction_text:
                LOGGER.info("Tier 1: Extracted %d chars from IUPAC location hint", len(extraction_text))
            else:
                LOGGER.warning("Tier 1: No text found at IUPAC location hint")
            # Add some manuscript context
            manuscript_text = "\n\n".join(self.ms_pages[:5])
        else:
            # Fallback to standard sections
            initial_sections = initial_sections or [
                "General procedure", "Compound characterization", 
                "Synthesis", "Experimental", "Materials and methods"
            ]
            
            # Extract from initial sections - search in all pages (manuscript + SI)
            extraction_text = self._extract_sections_by_title(initial_sections)
            
            # If no sections found by title, include first few SI pages which often have compound data
            if not extraction_text and self.si_pages:
                # SI often starts with compound characterization after TOC
                si_compound_pages = "\n\n".join(self.si_pages[2:10])  # Skip first 2 pages (usually TOC)
                extraction_text = si_compound_pages
            
            # Include manuscript pages (first 10) for model reaction context
            manuscript_text = "\n\n".join(self.ms_pages[:10])
        
        # Add campaign context if provided
        campaign_context = ""
        if campaign_filter:
            campaigns_warning = ""
            if self.all_campaigns:
                campaigns_warning = f"""
ALL CAMPAIGNS IN THIS PAPER:
{chr(10).join([f"- {campaign}" for campaign in self.all_campaigns])}

CRITICAL WARNING: Do NOT confuse campaigns! Each campaign uses completely different substrates.
"""
            
            campaign_context = f"""

IMPORTANT CAMPAIGN CONTEXT:
You are extracting compound information specifically for the {campaign_filter} campaign.
{campaigns_warning}
Focus ONLY on compound information relevant to the {campaign_filter} campaign/reaction system.
Do NOT include compound information from other campaigns.

"""
        
        # Combine manuscript text, campaign context, and extraction text
        if extraction_text:
            extraction_text = manuscript_text + campaign_context + "\n\n" + extraction_text
        else:
            extraction_text = manuscript_text + campaign_context
        
        # First extraction attempt - only for uncached compounds
        mappings = self._extract_compound_mappings_from_text(
            extraction_text[:50000], uncached_compound_ids, tag_suffix="initial", campaign_filter=campaign_filter
        )
        LOGGER.info("Tier 1: Found %d compound mappings from standard sections", len(mappings))
        
        # Check for missing compounds
        missing_compounds = []
        for cid in uncached_compound_ids:
            mapping = mappings.get(cid.lower().strip())
            if not mapping or not mapping.iupac_name:
                missing_compounds.append(cid)
        
        # Tier 2 (skip directly to full search): Full manuscript + SI search WITHOUT figures
        if missing_compounds:
            LOGGER.info("Tier 2: %d compounds still missing IUPAC names, going directly to full text search: %s", 
                       len(missing_compounds), sorted(missing_compounds))
            
            # Full text search including ALL pages (manuscript + SI)
            full_text = "\n\n".join(self.all_pages)  # Send everything
            
            # Use text-only extraction for Tier 2 (no images)
            final_mappings = self._extract_compound_mappings_from_text(
                full_text[:100000], missing_compounds, tag_suffix="tier2", campaign_filter=campaign_filter
            )
            
            # Merge final mappings with better compound ID matching
            final_found = 0
            for key, mapping in final_mappings.items():
                if key not in mappings or not mappings[key].iupac_name:
                    if mapping.iupac_name:
                        mappings[key] = mapping
                        final_found += 1
                        iupac_display = mapping.iupac_name[:50] + "..." if mapping.iupac_name and len(mapping.iupac_name) > 50 else (mapping.iupac_name or "None")
                        LOGGER.info("Found IUPAC name for '%s' in full search: %s", key, iupac_display)
            
            LOGGER.info("Tier 2: Found %d additional compound mappings", final_found)
        
        # Cache all newly found mappings using campaign-aware cache key
        for key, mapping in mappings.items():
            cache_key = f"{campaign_filter}_{key}" if campaign_filter else key
            if self._compound_mapping_cache.get(cache_key) is None:
                self._compound_mapping_cache.put(cache_key, mapping)
                iupac_display = mapping.iupac_name[:50] + "..." if mapping.iupac_name and len(mapping.iupac_name) > 50 else (mapping.iupac_name or "None")
                LOGGER.info("Cached compound mapping for: %s -> %s (campaign: %s)", key, iupac_display, campaign_filter)
                
                # Also cache without campaign prefix for backward compatibility during integration
                if campaign_filter:
                    self._compound_mapping_cache.put(key, mapping)
        
        # Combine cached and new mappings
        final_mappings = cached_mappings.copy()
        final_mappings.update(mappings)
        
        LOGGER.info("Adaptive compound mapping complete: %d total mappings (%d cached, %d new)", 
                   len(final_mappings), len(cached_mappings), len(mappings))
        return final_mappings

    def convert_pdf_to_images(self, pdf_pages: List[str], max_pages: int = 50) -> List[str]:
        """Convert PDF pages to base64-encoded PNG images.
        
        Args:
            pdf_pages: List of page text (used to determine page count)
            max_pages: Maximum number of pages to convert
            
        Returns:
            List of base64-encoded PNG strings
        """
        import base64
        
        # Open the manuscript PDF
        doc = fitz.open(self.ms_pdf_path)
        images = []
        
        try:
            page_count = min(len(pdf_pages), max_pages, doc.page_count)
            LOGGER.info("Converting %d manuscript pages to PNG images", page_count)
            
            for page_num in range(page_count):
                page = doc[page_num]
                # Render at 150 DPI for good quality/size balance
                pix = page.get_pixmap(dpi=150)
                
                # Convert to PNG
                img_data = pix.tobytes(output="png")
                img_base64 = base64.b64encode(img_data).decode('utf-8')
                images.append(img_base64)
                
            LOGGER.info("Successfully converted %d pages to PNG", len(images))
        finally:
            doc.close()
        
        return images

    def gather_model_reaction_info(self, enzyme_variants: Optional[List[str]] = None, lineage_compound_ids: Optional[Dict[str, List[str]]] = None) -> Dict[str, Any]:
        """Extract model reaction information using identified locations and 3-tier compound mapping."""
        # First find the best locations
        locations = self.find_model_reaction_locations(enzyme_variants)
        if not locations:
            LOGGER.warning("Could not find model reaction locations, using fallback approach")
            # Fallback to old approach but include more manuscript text
            pattern = re.compile(r"(model reaction|general procedure|typical .*run|standard conditions|scheme 1|figure 1)", re.I)
            snippets: List[str] = []
            # Search both manuscript and SI
            for page in self.all_pages:
                if pattern.search(page):
                    para_match = re.search(r"(.{0,3000}?\n\n)", page)
                    if para_match:
                        snippets.append(para_match.group(0))
                if len(snippets) >= 5:
                    break
            text_context = "\n---\n".join(snippets)[:10000]
        else:
            # Gather text from identified locations
            text_snippets = []
            
            # Always include manuscript abstract and introduction for context
            if self.ms_pages:
                # First 3 pages typically contain abstract, introduction, and model reaction info
                manuscript_intro = "\n\n".join(self.ms_pages[:3])
                text_snippets.append(f"=== MANUSCRIPT INTRODUCTION ===\n{manuscript_intro}")
            
            # Get model reaction context
            if locations.get("model_reaction_location", {}).get("location"):
                model_loc = locations["model_reaction_location"]["location"]
                LOGGER.info("Looking for model reaction at: %s", model_loc)
                model_text = self._get_text_around_location(model_loc)
                if model_text:
                    text_snippets.append(f"=== {model_loc} ===\n{model_text}")
            
            # Get conditions context  
            if locations.get("conditions_location", {}).get("location"):
                cond_loc = locations["conditions_location"]["location"]
                LOGGER.info("Looking for reaction conditions at: %s", cond_loc)
                cond_text = self._get_text_around_location(cond_loc)
                if cond_text:
                    text_snippets.append(f"=== {cond_loc} ===\n{cond_text}")
            
            # Get IUPAC names context from the specific location identified
            if locations.get("iupac_location", {}).get("location"):
                iupac_loc = locations["iupac_location"]["location"]
                
                # Handle case where iupac_loc is a list (multiple locations)
                iupac_locations = iupac_loc if isinstance(iupac_loc, list) else [iupac_loc]
                LOGGER.info("Looking for IUPAC names at: %s", iupac_locations)
                
                # If we have compound IDs from the model reaction location, search for them specifically
                compound_ids = locations.get("model_reaction_location", {}).get("compound_ids", [])
                if compound_ids:
                    LOGGER.info("Looking for specific compound IDs: %s", compound_ids)
                    # Search for each compound ID in the SI
                    for compound_id in compound_ids:
                        # Search patterns for compound characterization
                        patterns = [
                            rf"(?:compound\s+)?{re.escape(compound_id)}[:\s]*\([^)]+\)",  # 6a: (IUPAC name)
                            rf"(?:compound\s+)?{re.escape(compound_id)}[.\s]+[A-Z][^.]+",  # 6a. IUPAC name
                            rf"{re.escape(compound_id)}[^:]*:\s*[^.]+",  # Any format with colon
                        ]
                        
                        for page in self.si_pages:
                            for pattern in patterns:
                                match = re.search(pattern, page, re.I)
                                if match:
                                    # Get extended context around the match
                                    start = max(0, match.start() - 200)
                                    end = min(len(page), match.end() + 500)
                                    text_snippets.append(f"=== Compound {compound_id} characterization ===\n{page[start:end]}")
                                    break
                
                # Also search for substrate names mentioned in the reaction to find their IUPAC equivalents
                # Look for common substrate patterns in compound listings
                substrate_patterns = [
                    r"(?:substrate|reactant|reagent)s?\s*:?\s*([^.]+)",
                    r"(?:starting\s+material)s?\s*:?\s*([^.]+)",
                    r"\d+\.\s*([A-Za-z\s\-]+)(?:\s*\([^)]+\))?",  # numbered compound lists
                ]
                
                for pattern in substrate_patterns:
                    for page in self.si_pages[:5]:  # Check first few SI pages
                        matches = re.finditer(pattern, page, re.I)
                        for match in matches:
                            text = match.group(0)
                            if len(text) < 200:  # Reasonable length check
                                start = max(0, match.start() - 100)
                                end = min(len(page), match.end() + 300)
                                snippet = page[start:end]
                                if "prop-2-enoate" in snippet or "diazirin" in snippet:
                                    text_snippets.append(f"=== Substrate characterization ===\n{snippet}")
                                    break
                
                # Also get general IUPAC context for each location
                for loc in iupac_locations:
                    iupac_text = self._get_text_around_location(loc)
                    if iupac_text:
                        # Get more context around the identified location
                        extended_iupac_text = self._get_extended_text_around_location(loc, before=2000, after=10000)
                        if extended_iupac_text:
                            text_snippets.append(f"=== {loc} ===\n{extended_iupac_text}")
                        else:
                            text_snippets.append(f"=== {loc} ===\n{iupac_text}")
            
            text_context = "\n\n".join(text_snippets)[:35000]  # Increase limit for more context
        
        # Check document type and load appropriate PDF
        use_full_pdf = False
        pdf_data = None
        pdf_type = ""
        
        if locations:
            model_doc = locations.get("model_reaction_location", {}).get("document", "").lower()
            if model_doc == "manuscript":
                LOGGER.info("Model reaction is in manuscript - will send full manuscript as PDF")
                pdf_type = "manuscript"
                try:
                    if hasattr(self, 'ms_pdf_path') and self.ms_pdf_path:
                        with open(self.ms_pdf_path, 'rb') as pdf_file:
                            pdf_data = pdf_file.read()
                        LOGGER.info("Successfully loaded manuscript PDF (%d bytes) for model reaction extraction", len(pdf_data))
                        use_full_pdf = True
                    else:
                        LOGGER.warning("No manuscript PDF path available")
                except Exception as e:
                    LOGGER.warning("Failed to load manuscript PDF: %s", e)
            elif model_doc in ["supplementary", "si"]:
                LOGGER.info("Model reaction is in supplementary information - will send full SI as PDF")
                pdf_type = "supplementary"
                try:
                    if hasattr(self, 'si_pdf_path') and self.si_pdf_path:
                        with open(self.si_pdf_path, 'rb') as pdf_file:
                            pdf_data = pdf_file.read()
                        LOGGER.info("Successfully loaded SI PDF (%d bytes) for model reaction extraction", len(pdf_data))
                        use_full_pdf = True
                    else:
                        LOGGER.warning("No SI PDF path available")
                except Exception as e:
                    LOGGER.warning("Failed to load SI PDF: %s", e)
        
        # Extract figure images for model reaction if identified (and not using full PDF)
        figure_images = {}
        if locations and not use_full_pdf:
            # Extract images from model reaction and conditions locations
            for loc_key in ["model_reaction_location", "conditions_location"]:
                loc_info = locations.get(loc_key, {})
                location = loc_info.get("location", "")
                if location and ("figure" in location.lower() or "fig" in location.lower()):
                    # Extract just the figure reference (e.g., "Figure 2" from "Figure 2. Caption...")
                    fig_match = re.search(r"(Figure\s+\d+|Fig\s+\d+|Scheme\s+\d+)", location, re.I)
                    if fig_match:
                        fig_ref = fig_match.group(1)
                        LOGGER.info("Extracting image for %s from %s", fig_ref, loc_key)
                        img_b64 = self._extract_page_png(fig_ref, extract_figure_only=True)
                        if img_b64:
                            figure_images[fig_ref] = img_b64
                            LOGGER.info("Successfully extracted %s image for model reaction analysis", fig_ref)
        
        # Extract compound IDs from locations or use lineage-specific ones
        compound_ids = []
        if lineage_compound_ids:
            # Use lineage-specific compound IDs if provided
            substrate_ids = lineage_compound_ids.get("substrate_ids", [])
            product_ids = lineage_compound_ids.get("product_ids", [])
            compound_ids = substrate_ids + product_ids
            LOGGER.info("Using lineage-specific compound IDs: %s", compound_ids)
        elif locations and locations.get("model_reaction_location", {}).get("compound_ids"):
            compound_ids = locations["model_reaction_location"]["compound_ids"]
            LOGGER.info("Found compound IDs in model reaction: %s", compound_ids)
        
        # Use the 3-tier compound mapping approach if we have compound IDs
        compound_mappings = {}
        if compound_ids:
            LOGGER.info("Using 3-tier compound mapping approach for compounds: %s", compound_ids)
            
            # Pass the IUPAC location hint if we have it
            iupac_hint = locations.get("iupac_location") if locations else None
            compound_mappings = self._extract_compound_mappings_adaptive(
                compound_ids, 
                campaign_filter=self.campaign_filter,
                iupac_location_hint=iupac_hint
            )
            
            # Add the mapped IUPAC names to the context for better extraction
            if compound_mappings:
                mapping_text = "\n\n=== COMPOUND MAPPINGS ===\n"
                for cid in compound_ids:
                    mapping = compound_mappings.get(cid.lower().strip())
                    if mapping and mapping.iupac_name:
                        mapping_text += f"Compound {cid}: {mapping.iupac_name}\n"
                text_context += mapping_text
        
        # Add campaign context if available
        campaign_context = ""
        if enzyme_variants and self.campaign_filter:
            campaigns_context = ""
            if self.all_campaigns:
                campaigns_context = f"""
ALL CAMPAIGNS IN THIS PAPER:
{chr(10).join([f"- {campaign}" for campaign in self.all_campaigns])}

CRITICAL WARNING: Do NOT confuse campaigns! Each campaign uses completely different substrates:
- Different campaigns may use similar enzyme names but different substrates
- Be extremely careful to only extract data for the {self.campaign_filter} campaign
- Ignore data from other campaigns even if they seem similar
"""
            
            # Add specific campaign info if available
            campaign_info_context = ""
            if self.campaign_info:
                campaign_info_context = f"""

KNOWN CAMPAIGN INFORMATION:
- Campaign: {self.campaign_info.get('campaign_name', '')}
- Model Substrate: {self.campaign_info.get('model_substrate', '')} (ID: {self.campaign_info.get('substrate_id', '')})
- Model Product: {self.campaign_info.get('model_product', '')} (ID: {self.campaign_info.get('product_id', '')})
- Known Data Locations: {', '.join(self.campaign_info.get('data_locations', []))}

IMPORTANT: Use this information to guide your extraction. The model reaction should involve:
- Substrate ID: {self.campaign_info.get('substrate_id', '')}
- Product ID: {self.campaign_info.get('product_id', '')}
"""
            
            campaign_context = f"""
IMPORTANT CONTEXT:
You are extracting the model reaction used specifically for these enzyme variants:
{', '.join(enzyme_variants[:10])}{'...' if len(enzyme_variants) > 10 else ''}

These variants belong to campaign: {self.campaign_filter}
{campaigns_context}
{campaign_info_context}
Focus on extracting the model reaction that was used to evaluate THESE specific variants.
Different campaigns may use different model reactions and substrates.

CRITICAL: EXCLUDE reference variants from other publications!
- Only extract data for variants that were actually tested/created in THIS study
- Do NOT include data for reference enzymes cited from other papers
- Look for phrases like "from reference", "previously reported", "from [Author] et al." to identify reference variants
- Focus ONLY on the variants that were engineered/tested in this manuscript

"""
        
        # Include both manuscript and SI text for better coverage
        prompt = campaign_context + PROMPT_MODEL_REACTION + "\n\n=== CONTEXT ===\n" + text_context
        
        try:
            # Use multimodal extraction if we have figure images OR full PDF
            if figure_images or pdf_data:
                if pdf_data:
                    LOGGER.info("Using multimodal extraction with FULL %s PDF", pdf_type.upper())
                elif figure_images:
                    LOGGER.info("Using multimodal extraction with %d figure images", len(figure_images))
                
                # Prepare multimodal content
                if pdf_data:
                    # Modify prompt for full PDF
                    modified_prompt = prompt.replace(
                        "=== CONTEXT ===",
                        f"=== FULL {pdf_type.upper()} PDF ===\nThe attached PDF contains the complete {pdf_type}. Please analyze it to find the model reaction information.\n\n=== CONTEXT ==="
                    )
                    content_parts = [
                        modified_prompt,
                        {
                            "mime_type": "application/pdf",
                            "data": pdf_data
                        }
                    ]
                else:
                    content_parts = [prompt]
                
                # Add figure images if available and not using PDF
                if figure_images and not pdf_data:
                    for fig_ref, fig_base64 in figure_images.items():
                        try:
                            img_bytes = b64decode(fig_base64)
                            # Format image for Gemini API
                            image_part = {"mime_type": "image/png", "data": img_bytes}
                            content_parts.append(f"\n[Figure: {fig_ref}]")
                            content_parts.append(image_part)
                        except Exception as e:
                            LOGGER.warning("Failed to process figure %s: %s", fig_ref, e)
                
                # Use multimodal model if we have valid images
                if len(content_parts) > 1:
                    # Create multimodal request
                    model = genai.GenerativeModel(
                        model_name=self.cfg.model_name,
                        generation_config={
                            "temperature": self.cfg.model_reaction_temperature,
                            "top_p": self.cfg.top_p,
                            "top_k": 1,
                            "max_output_tokens": self.cfg.max_tokens,
                        }
                    )
                    
                    try:
                        response = model.generate_content(content_parts)
                        
                        # Track token usage if available
                        try:
                            if hasattr(response, 'usage_metadata'):
                                input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
                                output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)
                                if input_tokens or output_tokens:
                                    try:
                                        from .wrapper import add_token_usage
                                        add_token_usage('reaction_info_extractor', input_tokens, output_tokens)
                                    except ImportError:
                                        pass  # wrapper not available
                        except Exception:
                            pass  # token tracking is best-effort
                        
                        # Parse JSON from response
                        if response and response.text:
                            # Save debug output
                            if self.debug_dir:
                                timestamp = int(time.time())
                                mode_suffix = f"full_{pdf_type}_pdf" if pdf_data else "figures"
                                
                                # Save prompt with metadata
                                prompt_with_metadata = f"=== MODEL REACTION MULTIMODAL EXTRACTION ===\n"
                                prompt_with_metadata += f"Mode: {'FULL ' + pdf_type.upper() + ' PDF' if pdf_data else 'FIGURE EXTRACTION'}\n"
                                prompt_with_metadata += f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                                if pdf_data:
                                    prompt_with_metadata += f"{pdf_type.capitalize()} PDF size: {len(pdf_data)} bytes\n"
                                else:
                                    prompt_with_metadata += f"Figure images included: {len(figure_images)}\n"
                                    prompt_with_metadata += f"Figures: {', '.join(figure_images.keys())}\n"
                                prompt_with_metadata += "="*80 + "\n\n"
                                prompt_with_metadata += modified_prompt if pdf_data else prompt
                                
                                _dump(prompt_with_metadata, self.debug_dir / f"model_reaction_multimodal_{mode_suffix}_prompt_{timestamp}.txt")
                                _dump(response.text, self.debug_dir / f"model_reaction_multimodal_{mode_suffix}_response_{timestamp}.txt")
                            
                            # Extract JSON from response
                            text = response.text.strip()
                            if text.startswith("```json"):
                                text = text[7:]
                            if text.endswith("```"):
                                text = text[:-3]
                            data = json.loads(text.strip())
                        else:
                            raise ValueError("Empty response from multimodal model")
                    except Exception as vision_error:
                        LOGGER.error("Vision API call failed: %s", vision_error)
                        LOGGER.info("Falling back to text-only extraction")
                        # Fall back to text-only extraction
                        data = generate_json_with_retry(
                            self.model,
                            prompt,
                            temperature=self.cfg.model_reaction_temperature,
                            debug_dir=self.debug_dir,
                            tag="model_reaction_fallback"
                        )
                else:
                    # Fall back to text-only extraction
                    data = generate_json_with_retry(
                        self.model,
                        prompt,
                        temperature=self.cfg.model_reaction_temperature,
                        debug_dir=self.debug_dir,
                        tag="model_reaction"
                    )
            else:
                # Standard text-only extraction
                data = generate_json_with_retry(
                    self.model,
                    prompt,
                    temperature=self.cfg.model_reaction_temperature,
                    debug_dir=self.debug_dir,
                    tag="model_reaction"
                )
            
            # Handle the new array format for substrates/products
            if isinstance(data, dict):
                # If we have compound mappings, enhance the IUPAC names
                if compound_ids and compound_mappings:
                    LOGGER.info("Enhancing IUPAC names using compound mappings. Available mappings: %s", 
                               list(compound_mappings.keys()))
                    
                    # Try to map substrate/product lists through compound IDs
                    substrate_list = data.get("substrate_iupac_list", []) or data.get("substrate_list", [])
                    if isinstance(substrate_list, list):
                        enhanced_substrates = []
                        for item in substrate_list:
                            item_str = str(item).lower().strip()
                            # Check if it's a compound ID that we can map
                            mapping = compound_mappings.get(item_str)
                            if mapping and mapping.iupac_name:
                                enhanced_substrates.append(mapping.iupac_name)
                                LOGGER.info("Mapped substrate '%s' -> '%s'", item, mapping.iupac_name)
                            elif item and not re.match(r'^[0-9]+[a-z]?$|^S\d+$', str(item)):
                                # Keep valid IUPAC names that aren't compound IDs
                                enhanced_substrates.append(str(item))
                                LOGGER.info("Kept substrate IUPAC name: '%s'", item)
                            else:
                                LOGGER.warning("Could not map substrate compound ID '%s'", item)
                        data["substrate_iupac_list"] = enhanced_substrates
                    
                    product_list = data.get("product_iupac_list", []) or data.get("product_list", [])
                    if isinstance(product_list, list):
                        enhanced_products = []
                        for item in product_list:
                            item_str = str(item).lower().strip()
                            # Check if it's a compound ID that we can map
                            mapping = compound_mappings.get(item_str)
                            if mapping and mapping.iupac_name:
                                enhanced_products.append(mapping.iupac_name)
                                LOGGER.info("Mapped product '%s' -> '%s'", item, mapping.iupac_name)
                            elif item and not re.match(r'^[0-9]+[a-z]?$|^S\d+$', str(item)):
                                # Keep valid IUPAC names that aren't compound IDs
                                enhanced_products.append(str(item))
                                LOGGER.info("Kept product IUPAC name: '%s'", item)
                            else:
                                LOGGER.warning("Could not map product compound ID '%s'", item)
                        data["product_iupac_list"] = enhanced_products
                    
                    # Also try to enhance using both substrate_list and product_list if they contain compound IDs
                    for list_key, target_key in [("substrate_list", "substrate_iupac_list"), ("product_list", "product_iupac_list")]:
                        if list_key in data and isinstance(data[list_key], list):
                            if target_key not in data or not data[target_key]:
                                enhanced_list = []
                                for item in data[list_key]:
                                    item_str = str(item).lower().strip()
                                    mapping = compound_mappings.get(item_str)
                                    if mapping and mapping.iupac_name:
                                        enhanced_list.append(mapping.iupac_name)
                                        LOGGER.info("Enhanced %s: mapped '%s' -> '%s'", target_key, item, mapping.iupac_name)
                                if enhanced_list:
                                    data[target_key] = enhanced_list
                
                # Validate and convert arrays to semicolon-separated strings for CSV compatibility
                if "substrate_iupac_list" in data and isinstance(data["substrate_iupac_list"], list):
                    # Filter out non-IUPAC names (abbreviations like "1a", "S1", etc.)
                    valid_substrates = [s for s in data["substrate_iupac_list"] 
                                      if s and not re.match(r'^[0-9]+[a-z]?$|^S\d+$', s)]
                    # Join with semicolons instead of JSON encoding
                    data["substrate_iupac_list"] = "; ".join(valid_substrates) if valid_substrates else ""
                else:
                    data["substrate_iupac_list"] = ""
                    
                if "product_iupac_list" in data and isinstance(data["product_iupac_list"], list):
                    # Filter out non-IUPAC names
                    valid_products = [p for p in data["product_iupac_list"] 
                                    if p and not re.match(r'^[0-9]+[a-z]?$|^S\d+$', p)]
                    # Join with semicolons instead of JSON encoding
                    data["product_iupac_list"] = "; ".join(valid_products) if valid_products else ""
                else:
                    data["product_iupac_list"] = ""
                    
        except Exception as exc:
            LOGGER.error("Failed to extract model reaction: %s", exc)
            data = {
                "substrate_iupac_list": None,
                "product_iupac_list": None,
                "reaction_substrate_concentration": None,
                "cofactor": None,
                "reaction_temperature": None,
                "reaction_ph": None,
                "reaction_buffer": None,
                "reaction_other_conditions": None,
                "error": str(exc)
            }
        
        # Ensure all expected keys are present
        expected_keys = [
            "substrate_list", "substrate_iupac_list", "product_list", "product_iupac_list", 
            "reaction_substrate_concentration", "cofactor", "reaction_temperature", 
            "reaction_ph", "reaction_buffer", "reaction_other_conditions"
        ]
        for key in expected_keys:
            data.setdefault(key, None)
        
        # === OPSIN VALIDATION AND COMPOUND MAPPING FALLBACK ===
        # Check if the IUPAC names are actually valid using OPSIN
        needs_compound_mapping = False
        
        # Check substrate IUPAC names
        substrate_has_invalid = False
        if data.get("substrate_list") and isinstance(data["substrate_list"], list):
            # Check if we have substrate IDs but missing or invalid IUPAC names
            if not data.get("substrate_iupac_list"):
                LOGGER.warning("Substrate list exists but no IUPAC names provided")
                substrate_has_invalid = True
            else:
                substrate_names = data["substrate_iupac_list"].split("; ") if isinstance(data["substrate_iupac_list"], str) else []
                # Check each substrate ID has a valid IUPAC name
                for i, substrate_id in enumerate(data["substrate_list"]):
                    if i >= len(substrate_names) or not substrate_names[i]:
                        LOGGER.warning(f"No IUPAC name for substrate '{substrate_id}'")
                        substrate_has_invalid = True
                    elif not is_valid_iupac_name_with_opsin(substrate_names[i]):
                        LOGGER.warning(f"Invalid IUPAC name detected for substrate '{substrate_id}': '{substrate_names[i]}'")
                        substrate_has_invalid = True
            
            if substrate_has_invalid:
                needs_compound_mapping = True
                LOGGER.info("Found missing or invalid substrate IUPAC names, will attempt compound mapping")
        
        # Check product IUPAC names
        product_has_invalid = False
        if data.get("product_list") and isinstance(data["product_list"], list):
            # Check if we have product IDs but missing or invalid IUPAC names
            if not data.get("product_iupac_list"):
                LOGGER.warning("Product list exists but no IUPAC names provided")
                product_has_invalid = True
            else:
                product_names = data["product_iupac_list"].split("; ") if isinstance(data["product_iupac_list"], str) else []
                # Check each product ID has a valid IUPAC name
                for i, product_id in enumerate(data["product_list"]):
                    if i >= len(product_names) or not product_names[i]:
                        LOGGER.warning(f"No IUPAC name for product '{product_id}'")
                        product_has_invalid = True
                    elif not is_valid_iupac_name_with_opsin(product_names[i]):
                        LOGGER.warning(f"Invalid IUPAC name detected for product '{product_id}': '{product_names[i]}'")
                        product_has_invalid = True
            
            if product_has_invalid:
                needs_compound_mapping = True
                LOGGER.info("Found missing or invalid product IUPAC names, will attempt compound mapping")
        
        # If we need compound mapping and have substrate/product lists, attempt it
        if needs_compound_mapping and (data.get("substrate_list") or data.get("product_list")):
            LOGGER.info("Attempting compound mapping due to invalid IUPAC names")
            
            # Collect all compound IDs that need mapping
            compound_ids_to_map = []
            if data.get("substrate_list") and isinstance(data["substrate_list"], list):
                compound_ids_to_map.extend(data["substrate_list"])
            if data.get("product_list") and isinstance(data["product_list"], list):
                compound_ids_to_map.extend(data["product_list"])
            
            if compound_ids_to_map:
                LOGGER.info(f"Attempting to map compound IDs: {compound_ids_to_map}")
                
                # Use the adaptive compound mapping
                compound_mappings = self._extract_compound_mappings_adaptive(
                    compound_ids_to_map,
                    campaign_filter=self.campaign_filter
                )
                
                # Re-map substrate IUPAC names
                if data.get("substrate_list") and isinstance(data["substrate_list"], list):
                    mapped_substrates = []
                    for substrate_id in data["substrate_list"]:
                        mapping = compound_mappings.get(substrate_id.lower().strip())
                        if mapping and mapping.iupac_name and is_valid_iupac_name_with_opsin(mapping.iupac_name):
                            mapped_substrates.append(mapping.iupac_name)
                            LOGGER.info(f"Successfully mapped substrate '{substrate_id}' to IUPAC: {mapping.iupac_name}")
                    
                    if mapped_substrates:
                        data["substrate_iupac_list"] = "; ".join(mapped_substrates)
                        LOGGER.info(f"Updated substrate IUPAC list with {len(mapped_substrates)} valid names")
                
                # Re-map product IUPAC names
                if data.get("product_list") and isinstance(data["product_list"], list):
                    mapped_products = []
                    for product_id in data["product_list"]:
                        mapping = compound_mappings.get(product_id.lower().strip())
                        if mapping and mapping.iupac_name and is_valid_iupac_name_with_opsin(mapping.iupac_name):
                            mapped_products.append(mapping.iupac_name)
                            LOGGER.info(f"Successfully mapped product '{product_id}' to IUPAC: {mapping.iupac_name}")
                    
                    if mapped_products:
                        data["product_iupac_list"] = "; ".join(mapped_products)
                        LOGGER.info(f"Updated product IUPAC list with {len(mapped_products)} valid names")
            
        return data

    def _process_single_lineage(self, location: Dict[str, Any], enzyme_df: pd.DataFrame) -> pd.DataFrame:
        """Process a single lineage case - use confidence-based processing."""
        # Create lineage analysis for single location
        lineage_analysis = {
            'has_multiple_lineages': False,
            'lineage_groups': [{
                'group_id': self._get_base_location(location['location']),
                'data_location': location['location'],
                'lineage_hint': location.get('lineage_hint', ''),
                'caption': location.get('caption', ''),
                'confidence': location.get('confidence', 0)
            }]
        }
        
        return self._process_multiple_lineages_by_confidence([location], enzyme_df, lineage_analysis)
    
    def _process_multiple_lineages_by_confidence(self, locations: List[Dict[str, Any]], 
                                                 enzyme_df: pd.DataFrame,
                                                 lineage_analysis: Dict[str, Any]) -> pd.DataFrame:
        """Process multiple lineages by confidence, detecting which enzymes belong to which campaign."""
        # Get all enzyme IDs
        all_enzyme_ids = enzyme_df['enzyme_id'].tolist() if 'enzyme_id' in enzyme_df.columns else enzyme_df['enzyme'].tolist()
        all_variants = set(all_enzyme_ids)
        variants_with_data = set()
        all_results = []
        
        # If enzyme_df has campaign_id column, we can use it to filter
        has_campaign_info = 'campaign_id' in enzyme_df.columns
        
        # Select the most confident source only
        best_location = None
        if locations:
            # Sort by confidence only
            locations_sorted = sorted(locations, key=lambda x: -x.get('confidence', 0))
            best_location = locations_sorted[0]
            
            LOGGER.info("Selected primary location: %s (type: %s, confidence: %d%%)", 
                       best_location['location'], 
                       best_location.get('type', 'unknown'), 
                       best_location.get('confidence', 0))
            
            # Extract metrics from the most confident source only
            # Pass all locations so Gemini can check them all
            best_location['all_locations'] = locations_sorted
            metrics_rows = self.extract_metrics_batch(all_enzyme_ids, best_location)
            
            # Filter to valid metrics
            valid_metrics = [m for m in metrics_rows if self._has_valid_metrics(m)]
            
            if not valid_metrics:
                LOGGER.warning("No valid metrics found in primary location %s", best_location['location'])
                return pd.DataFrame()
                
            LOGGER.info("Found %d enzymes with data in %s", len(valid_metrics), best_location['location'])
            
            # Create DataFrame for the single best location
            df_location = pd.DataFrame(valid_metrics)
            
            # Add metadata about the location
            df_location['data_location'] = best_location['location']
            df_location['confidence'] = best_location.get('confidence', 0)
            
            LOGGER.info("Successfully extracted data for %d enzymes from primary location", len(df_location))
            
            # Extract model reaction info once for this location
            location_context = f"Location: {best_location['location']}"
            if best_location.get('caption'):
                location_context += f"\nCaption: {best_location['caption']}"
            
            # Get enzyme list for model reaction  
            location_enzymes = df_location['enzyme'].unique().tolist()
            # Get model reaction locations for this campaign
            model_reaction_locations = self.find_model_reaction_locations(location_enzymes)
            
            # Extract model reaction for this location - use unified approach
            LOGGER.info("Extracting model reaction for location: %s", best_location['location'])
            
            # Skip lineage-specific extraction and use comprehensive multimodal extraction directly
            # The lineage-specific extraction often returns generic substrate classes instead of specific compounds
            LOGGER.info("Using comprehensive multimodal extraction for model reaction")
            model_info = self.gather_model_reaction_info(location_enzymes)
                
            LOGGER.info("Model reaction extraction complete for location: %s", best_location['location'])
            
            # Add model reaction info to all enzymes from this location
            for key, value in model_info.items():
                if isinstance(value, list):
                    value = "; ".join(str(v) for v in value) if value else None
                df_location[key] = value
            
            # Add additional location metadata (data_location already set above)
            df_location['location_type'] = best_location.get('type', 'unknown')
            df_location['location_confidence'] = best_location.get('confidence', 0)
            
            LOGGER.info("Extraction complete: %d variants from primary location %s", 
                       len(df_location), best_location['location'])
            
            return df_location
        
        # No locations found
        LOGGER.warning("No valid locations found for extraction")
        return pd.DataFrame()
    
    def _has_valid_metrics(self, metrics_row: Dict[str, Any]) -> bool:
        """Check if a metrics row contains any valid performance data."""
        metric_fields = ['yield', 'ttn', 'ton', 'selectivity', 'conversion', 'tof', 'activity']
        
        for field in metric_fields:
            if metrics_row.get(field) is not None:
                return True
                
        # Also check other_metrics
        if metrics_row.get('other_metrics') and isinstance(metrics_row['other_metrics'], dict):
            if metrics_row['other_metrics']:  # Non-empty dict
                return True
                
        return False
    
    def _filter_locations_by_campaign(self, locations: List[Dict[str, Any]], 
                                     enzyme_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Filter locations to only those relevant to the current campaign."""
        if not self.campaign_filter or 'campaign_id' not in enzyme_df.columns:
            return locations
        
        # Get enzyme names for this campaign
        campaign_enzymes = enzyme_df[enzyme_df['campaign_id'] == self.campaign_filter]['enzyme_id' if 'enzyme_id' in enzyme_df.columns else 'enzyme'].tolist()
        
        # Extract any common patterns from enzyme names
        enzyme_patterns = set()
        for enzyme in campaign_enzymes:
            # Extract any uppercase abbreviations (e.g., 'PYS', 'INS')
            matches = re.findall(r'[A-Z]{2,}', enzyme)
            enzyme_patterns.update(matches)
        
        LOGGER.info("Campaign %s has enzyme patterns: %s", self.campaign_filter, enzyme_patterns)
        
        # Get campaign description keywords from the campaign data if available
        campaign_keywords = set()
        # Extract keywords from campaign_id (e.g., 'pyrrolidine_synthase_evolution' -> ['pyrrolidine', 'synthase'])
        words = self.campaign_filter.lower().replace('_', ' ').split()
        # Filter out generic words
        generic_words = {'evolution', 'campaign', 'synthase', 'enzyme', 'variant'}
        campaign_keywords.update(word for word in words if word not in generic_words and len(word) > 3)
        
        LOGGER.info("Campaign keywords: %s", campaign_keywords)
        
        # Filter locations based on campaign clues
        filtered = []
        for loc in locations:
            # Check caption and clues for campaign indicators
            caption = (loc.get('caption') or '').lower()
            campaign_clues = (loc.get('campaign_clues') or '').lower()
            lineage_hint = (loc.get('lineage_hint') or '').lower()
            combined_text = caption + ' ' + campaign_clues + ' ' + lineage_hint
            
            # Check if location is relevant to this campaign
            is_relevant = False
            
            # Check for enzyme patterns
            for pattern in enzyme_patterns:
                if pattern.lower() in combined_text:
                    is_relevant = True
                    break
            
            # Check for campaign keywords
            if not is_relevant:
                for keyword in campaign_keywords:
                    if keyword in combined_text:
                        is_relevant = True
                        break
            
            # Check if any campaign enzymes are explicitly mentioned
            if not is_relevant:
                for enzyme in campaign_enzymes[:5]:  # Check first few enzymes
                    if enzyme.lower() in combined_text:
                        is_relevant = True
                        break
            
            if is_relevant:
                filtered.append(loc)
                LOGGER.info("Location %s is relevant to campaign %s", 
                           loc.get('location'), self.campaign_filter)
            else:
                LOGGER.debug("Location %s filtered out for campaign %s", 
                            loc.get('location'), self.campaign_filter)
        
        return filtered
    
    def _extract_lineage_model_info(self, lineage_reaction: Dict[str, Any], enzyme_variants: Optional[List[str]] = None) -> Dict[str, Any]:
        """Extract full model reaction info including IUPAC names for a lineage."""
        # Get substrate/product IDs from lineage-specific extraction
        substrate_ids = lineage_reaction.get('substrate_ids', [])
        product_ids = lineage_reaction.get('product_ids', [])
        
        # Get general model reaction info for conditions, using lineage-specific compound IDs
        lineage_ids = {
            "substrate_ids": substrate_ids,
            "product_ids": product_ids
        }
        general_info = self.gather_model_reaction_info(enzyme_variants, lineage_compound_ids=lineage_ids)
        
        # Override substrate/product lists with lineage-specific ones only if they contain actual compound IDs
        model_info = general_info.copy()
        
        # Check if substrate_ids contain actual compound IDs (not generic terms like "alkyl azide")
        if substrate_ids and any(re.match(r'^[0-9]+[a-z]?$|^[A-Z][0-9]+$', sid) for sid in substrate_ids):
            model_info['substrate_list'] = substrate_ids
        elif not substrate_ids and general_info.get('substrate_list'):
            # Keep the general info if lineage extraction found nothing
            pass
        else:
            model_info['substrate_list'] = substrate_ids
            
        # Check if product_ids contain actual compound IDs (not generic terms like "pyrrolidine")
        if product_ids and any(re.match(r'^[0-9]+[a-z]?$|^[A-Z][0-9]+$', pid) for pid in product_ids):
            model_info['product_list'] = product_ids
        elif not product_ids and general_info.get('product_list'):
            # Keep the general info if lineage extraction found nothing
            pass
        else:
            # If we only have generic terms, try to keep general info if available
            if general_info.get('product_list') and all(len(pid) > 5 for pid in product_ids):
                # Likely generic terms like "pyrrolidine", keep general info
                pass
            else:
                model_info['product_list'] = product_ids
        
        # Extract IUPAC names for the compounds we're actually using
        # Use the IDs from model_info (which may have been preserved from general extraction)
        final_substrate_ids = model_info.get('substrate_list', [])
        final_product_ids = model_info.get('product_list', [])
        all_compound_ids = final_substrate_ids + final_product_ids
        
        if all_compound_ids:
            compound_mappings = self._extract_compound_mappings_adaptive(all_compound_ids)
            
            # Map substrate IUPAC names
            substrate_iupacs = []
            for sid in final_substrate_ids:
                mapping = compound_mappings.get(str(sid).lower().strip())
                if mapping and mapping.iupac_name:
                    substrate_iupacs.append(mapping.iupac_name)
            # Only update if we found IUPAC names
            if substrate_iupacs:
                model_info['substrate_iupac_list'] = substrate_iupacs
            
            # Map product IUPAC names
            product_iupacs = []
            for pid in final_product_ids:
                mapping = compound_mappings.get(str(pid).lower().strip())
                if mapping and mapping.iupac_name:
                    product_iupacs.append(mapping.iupac_name)
            # Only update if we found IUPAC names
            if product_iupacs:
                model_info['product_iupac_list'] = product_iupacs
        
        return model_info
    
    def _process_single_lineage_by_confidence(self, locations: List[Dict[str, Any]], 
                                             enzyme_df: pd.DataFrame) -> pd.DataFrame:
        """Process single lineage by confidence, stopping when all variants have data."""
        # Get list of all variants we need data for
        all_variants = set(enzyme_df['enzyme'].tolist() if 'enzyme' in enzyme_df.columns else 
                          enzyme_df['enzyme_id'].tolist())
        variants_with_data = set()
        all_results = []
        
        # Process locations in order of confidence
        for location in locations:
            if len(variants_with_data) >= len(all_variants):
                LOGGER.info("All variants have data, stopping extraction")
                break
                
            LOGGER.info("\nProcessing location %s (confidence: %d%%)", 
                       location['location'], location.get('confidence', 0))
            
            # Extract metrics from this location
            metrics_rows = self.extract_metrics_batch(list(all_variants), location)
            
            # Filter to valid metrics
            valid_metrics = [m for m in metrics_rows if self._has_valid_metrics(m)]
            
            if not valid_metrics:
                LOGGER.warning("No valid metrics found in %s", location['location'])
                continue
            
            # Create DataFrame for this location
            df_location = pd.DataFrame(valid_metrics)
            
            # Track which variants we got data for
            new_variants = set(df_location['enzyme'].tolist()) - variants_with_data
            LOGGER.info("Found data for %d new variants in %s", len(new_variants), location['location'])
            variants_with_data.update(new_variants)
            
            # Add location info
            df_location['data_location'] = location['location']
            df_location['location_type'] = location.get('type', 'unknown')
            df_location['location_confidence'] = location.get('confidence', 0)
            
            all_results.append(df_location)
            
            # Log progress
            LOGGER.info("Progress: %d/%d variants have data", 
                       len(variants_with_data), len(all_variants))
        
        if all_results:
            # Combine all results
            df_combined = pd.concat(all_results, ignore_index=True)
            
            # If we have duplicates (same variant in multiple locations), keep the one with highest confidence
            if df_combined.duplicated(subset=['enzyme']).any():
                LOGGER.info("Removing duplicates, keeping highest confidence data")
                df_combined = df_combined.sort_values(
                    ['enzyme', 'location_confidence'], 
                    ascending=[True, False]
                ).drop_duplicates(subset=['enzyme'], keep='first')
            
            # Extract model reaction info once
            # Pass the enzyme variants we're processing
            enzyme_list = df_combined['enzyme'].unique().tolist()
            model_info = self.gather_model_reaction_info(enzyme_list)
            
            # Add model reaction info to all rows
            for key, value in model_info.items():
                if isinstance(value, list):
                    value = "; ".join(str(v) for v in value) if value else None
                df_combined[key] = value
            
            LOGGER.info("Extraction complete: %d unique variants with data", len(df_combined))
            
            return df_combined
        else:
            LOGGER.warning("No metrics extracted from any location")
            return pd.DataFrame()

    # ------------------------------------------------------------------
    # 6.5 Public orchestrator
    # ------------------------------------------------------------------

    def run(self, enzyme_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        # This module should always have enzyme CSV provided
        if enzyme_df is None:
            LOGGER.error("No enzyme DataFrame provided - this module requires enzyme CSV input")
            return pd.DataFrame()
        
        # Store enzyme_df for use in extract_metrics_batch
        self.enzyme_df = enzyme_df
        
        # Check if we have campaign_id column - if so, process each campaign separately
        if 'campaign_id' in enzyme_df.columns and not self.campaign_filter:
            campaigns = enzyme_df['campaign_id'].unique()
            if len(campaigns) > 1:
                LOGGER.info("Detected %d campaigns in enzyme data - processing each separately", len(campaigns))
                all_campaign_results = []
                
                for campaign_id in campaigns:
                    LOGGER.info("\n" + "="*60)
                    LOGGER.info("Processing campaign: %s", campaign_id)
                    LOGGER.info("="*60)
                    
                    # Create a new extractor instance for this campaign
                    campaign_extractor = ReactionExtractor(
                        manuscript=self.manuscript,
                        si=self.si,
                        cfg=self.cfg,
                        debug_dir=self.debug_dir / campaign_id if self.debug_dir else None,
                        campaign_filter=campaign_id,
                        all_campaigns=campaigns.tolist()
                    )
                    
                    # Run extraction for this campaign
                    campaign_df = campaign_extractor.run(enzyme_df)
                    
                    if not campaign_df.empty:
                        # Add a temporary campaign identifier for merging
                        campaign_df['_extraction_campaign'] = campaign_id
                        all_campaign_results.append(campaign_df)
                        LOGGER.info("Extracted %d reactions for campaign %s", len(campaign_df), campaign_id)
                
                # Combine results from all campaigns
                if all_campaign_results:
                    combined_df = pd.concat(all_campaign_results, ignore_index=True)
                    LOGGER.info("\nCombined extraction complete: %d total reactions across %d campaigns", 
                               len(combined_df), len(campaigns))
                    return combined_df
                else:
                    LOGGER.warning("No reactions extracted from any campaign")
                    return pd.DataFrame()
        
        # Filter by campaign if specified
        if self.campaign_filter and 'campaign_id' in enzyme_df.columns:
            LOGGER.info("Filtering enzymes for campaign: %s", self.campaign_filter)
            enzyme_df = enzyme_df[enzyme_df['campaign_id'] == self.campaign_filter].copy()
            LOGGER.info("Found %d enzymes for campaign %s", len(enzyme_df), self.campaign_filter)
            if len(enzyme_df) == 0:
                LOGGER.warning("No enzymes found for campaign %s", self.campaign_filter)
                return pd.DataFrame()
        
        # Find all locations with performance data
        locations = self.find_reaction_locations()
        if not locations:
            LOGGER.error("Failed to find reaction data locations")
            return pd.DataFrame()
        
        # Filter locations by campaign if specified
        if self.campaign_filter:
            filtered_locations = self._filter_locations_by_campaign(locations, enzyme_df)
            if filtered_locations:
                LOGGER.info("Filtered to %d locations for campaign %s", 
                           len(filtered_locations), self.campaign_filter)
                locations = filtered_locations
            else:
                LOGGER.warning("No locations found specifically for campaign %s, using all locations", 
                             self.campaign_filter)
        
        # Sort locations by confidence (highest first) and prefer tables over figures
        locations_sorted = sorted(locations, key=lambda x: (
            x.get('confidence', 0),
            1 if x.get('type') == 'table' else 0  # Prefer tables when confidence is equal
        ), reverse=True)
        
        LOGGER.info("Found %d reaction data location(s), sorted by confidence:", len(locations_sorted))
        for loc in locations_sorted:
            LOGGER.info("  - %s (%s, confidence: %d%%)", 
                       loc.get('location'), 
                       loc.get('type'),
                       loc.get('confidence', 0))
            
        # Analyze if we have multiple lineages
        lineage_analysis = self.analyze_lineage_groups(locations_sorted, enzyme_df)
        has_multiple_lineages = lineage_analysis.get('has_multiple_lineages', False)
        
        if has_multiple_lineages:
            LOGGER.info("Multiple lineage groups detected")
            return self._process_multiple_lineages_by_confidence(locations_sorted, enzyme_df, lineage_analysis)
        else:
            LOGGER.info("Single lineage detected, using confidence-based processing")
            return self._process_single_lineage_by_confidence(locations_sorted, enzyme_df)

###############################################################################
# 7 - MERGE WITH LINEAGE CSV + SAVE
###############################################################################

def merge_with_lineage_data(
    df_lineage: pd.DataFrame, df_metrics: pd.DataFrame
) -> pd.DataFrame:
    """Merge lineage and metrics data ensuring one-to-one mapping per campaign."""
    
    # Handle both 'enzyme' and 'enzyme_id' column names
    if "enzyme_id" in df_lineage.columns and "enzyme" not in df_lineage.columns:
        df_lineage = df_lineage.rename(columns={"enzyme_id": "enzyme"})
    
    if "enzyme" not in df_lineage.columns:
        raise ValueError("Lineage CSV must have an 'enzyme' or 'enzyme_id' column.")
    
    # Check if we have campaign information to match on
    if "campaign_id" in df_lineage.columns and "_extraction_campaign" in df_metrics.columns:
        # Match on both enzyme and campaign to ensure correct pairing
        df_metrics_temp = df_metrics.copy()
        df_metrics_temp['campaign_id'] = df_metrics_temp['_extraction_campaign']
        df_metrics_temp = df_metrics_temp.drop('_extraction_campaign', axis=1)
        merged = df_lineage.merge(df_metrics_temp, on=["enzyme", "campaign_id"], how="left")
    else:
        # Simple merge on enzyme only
        if "_extraction_campaign" in df_metrics.columns:
            df_metrics = df_metrics.drop('_extraction_campaign', axis=1)
        merged = df_lineage.merge(df_metrics, on="enzyme", how="left")
    
    return merged

###############################################################################
# 8 - CLI ENTRY-POINT
###############################################################################

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Extract enzyme reaction metrics from chemistry PDFs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--manuscript", required=True, type=Path)
    p.add_argument("--si", type=Path, help="Supporting-information PDF")
    p.add_argument("--lineage-csv", type=Path)
    p.add_argument("--output", type=Path, default=Path("reaction_metrics.csv"))
    p.add_argument("--verbose", action="store_true")
    p.add_argument(
        "--debug-dir",
        metavar="DIR",
        help="Write ALL intermediate artefacts (prompts, raw Gemini replies) to DIR",
    )
    return p

def main() -> None:
    args = build_parser().parse_args()
    if args.verbose:
        LOGGER.setLevel(logging.DEBUG)
    cfg = Config()
    
    # Load enzyme data from CSV if provided to detect campaign information
    enzyme_df = None
    campaign_filter = None
    all_campaigns = None
    
    if args.lineage_csv and args.lineage_csv.exists():
        LOGGER.info("Loading enzyme data from CSV…")
        enzyme_df = pd.read_csv(args.lineage_csv)
        
        # Rename enzyme_id to enzyme if needed
        if "enzyme_id" in enzyme_df.columns and "enzyme" not in enzyme_df.columns:
            enzyme_df = enzyme_df.rename(columns={"enzyme_id": "enzyme"})
            LOGGER.info("Renamed 'enzyme_id' column to 'enzyme' in lineage data")
        
        # Detect campaign information from the enzyme CSV
        if 'campaign_id' in enzyme_df.columns:
            all_campaigns = enzyme_df['campaign_id'].dropna().unique().tolist()
            if len(all_campaigns) == 1:
                campaign_filter = all_campaigns[0]
                LOGGER.info("Detected single campaign: %s", campaign_filter)
                
                # Create campaign-specific debug directory even for single campaign
                campaign_debug_dir = None
                if args.debug_dir:
                    campaign_debug_dir = Path(args.debug_dir) / f"campaign_{campaign_filter}"
                    campaign_debug_dir.mkdir(parents=True, exist_ok=True)
                    LOGGER.info("Campaign debug directory: %s", campaign_debug_dir)
                
                # Load campaign info from campaigns.json if available
                campaign_info = None
                if args.debug_dir:
                    from .campaign_utils import load_campaigns_from_file, find_campaign_by_id
                    campaigns_file = Path(args.debug_dir) / "campaigns.json"
                    if campaigns_file.exists():
                        campaigns = load_campaigns_from_file(campaigns_file)
                        campaign_info = find_campaign_by_id(campaigns, campaign_filter)
                        if campaign_info:
                            LOGGER.info("Loaded campaign info for %s from campaigns.json", campaign_filter)
                
                extractor = ReactionExtractor(args.manuscript, args.si, cfg, debug_dir=campaign_debug_dir, 
                                            campaign_filter=campaign_filter, all_campaigns=all_campaigns,
                                            campaign_info=campaign_info)
                df_metrics = extractor.run(enzyme_df)
                
                # For single campaign, also merge with lineage data
                if not df_metrics.empty:
                    df_metrics = df_metrics.merge(enzyme_df, on='enzyme', how='left', suffixes=('', '_lineage'))
                    LOGGER.info("Merged metrics with lineage data for single campaign")
                
            elif len(all_campaigns) > 1:
                LOGGER.info("Detected multiple campaigns: %s", all_campaigns)
                all_results = []
                
                # Process each campaign separately
                for campaign in all_campaigns:
                    LOGGER.info("Processing campaign: %s", campaign)
                    
                    # Filter enzyme_df to this campaign
                    campaign_df = enzyme_df[enzyme_df['campaign_id'] == campaign].copy()
                    LOGGER.info("Found %d enzymes for campaign %s", len(campaign_df), campaign)
                    
                    if len(campaign_df) == 0:
                        LOGGER.warning("No enzymes found for campaign %s, skipping", campaign)
                        continue
                    
                    # Create extractor for this campaign with campaign-specific debug directory
                    campaign_debug_dir = None
                    if args.debug_dir:
                        campaign_debug_dir = Path(args.debug_dir) / f"campaign_{campaign}"
                        campaign_debug_dir.mkdir(parents=True, exist_ok=True)
                        LOGGER.info("Campaign debug directory: %s", campaign_debug_dir)
                    
                    # Load campaign info from campaigns.json if available
                    campaign_info = None
                    if args.debug_dir:
                        from .campaign_utils import load_campaigns_from_file, find_campaign_by_id
                        campaigns_file = Path(args.debug_dir) / "campaigns.json"
                        if campaigns_file.exists():
                            campaigns = load_campaigns_from_file(campaigns_file)
                            campaign_info = find_campaign_by_id(campaigns, campaign)
                            if campaign_info:
                                LOGGER.info("Loaded campaign info for %s from campaigns.json", campaign)
                    
                    extractor = ReactionExtractor(args.manuscript, args.si, cfg, debug_dir=campaign_debug_dir, 
                                                campaign_filter=campaign, all_campaigns=all_campaigns,
                                                campaign_info=campaign_info)
                    
                    # Run extraction for this campaign
                    campaign_metrics = extractor.run(campaign_df)
                    
                    if not campaign_metrics.empty:
                        # Merge with lineage data for this campaign
                        campaign_lineage = enzyme_df[enzyme_df['campaign_id'] == campaign].copy()
                        if "enzyme_id" in campaign_lineage.columns and "enzyme" not in campaign_lineage.columns:
                            campaign_lineage = campaign_lineage.rename(columns={"enzyme_id": "enzyme"})
                        
                        # Merge campaign metrics with lineage data
                        campaign_final = campaign_metrics.merge(campaign_lineage, on='enzyme', how='left', suffixes=('', '_lineage'))
                        
                        # Rename aa_seq to protein_sequence for consistency
                        if 'aa_seq' in campaign_final.columns:
                            campaign_final = campaign_final.rename(columns={'aa_seq': 'protein_sequence'})
                        
                        # Save campaign-specific file immediately
                        output_dir = args.output.parent
                        base_name = args.output.stem
                        campaign_file = output_dir / f"{base_name}_{campaign}.csv"
                        campaign_final.to_csv(campaign_file, index=False)
                        LOGGER.info("Saved %d rows for campaign %s -> %s", len(campaign_final), campaign, campaign_file)
                        
                        # Add the merged data (not just metrics) to final results
                        all_results.append(campaign_final)
                        LOGGER.info("Added %d merged results for campaign %s", len(campaign_final), campaign)
                    else:
                        LOGGER.warning("No results extracted for campaign %s", campaign)
                        
                        # Still save an empty campaign file with lineage data
                        campaign_lineage = enzyme_df[enzyme_df['campaign_id'] == campaign].copy()
                        if not campaign_lineage.empty:
                            # Rename aa_seq to protein_sequence for consistency
                            if 'aa_seq' in campaign_lineage.columns:
                                campaign_lineage = campaign_lineage.rename(columns={'aa_seq': 'protein_sequence'})
                            
                            output_dir = args.output.parent
                            base_name = args.output.stem
                            campaign_file = output_dir / f"{base_name}_{campaign}.csv"
                            campaign_lineage.to_csv(campaign_file, index=False)
                            LOGGER.info("Saved %d rows (lineage only) for campaign %s -> %s", len(campaign_lineage), campaign, campaign_file)
                
                # Combine all campaign results
                if all_results:
                    df_metrics = pd.concat(all_results, ignore_index=True)
                    LOGGER.info("Combined results from %d campaigns: %d total rows", len(all_results), len(df_metrics))
                else:
                    LOGGER.warning("No results from any campaign")
                    df_metrics = pd.DataFrame()
        else:
            # No campaign information, process all enzymes together
            campaign_debug_dir = None
            if args.debug_dir:
                campaign_debug_dir = Path(args.debug_dir) / "no_campaign"
                campaign_debug_dir.mkdir(parents=True, exist_ok=True)
                LOGGER.info("Debug directory (no campaign): %s", campaign_debug_dir)
            
            extractor = ReactionExtractor(args.manuscript, args.si, cfg, debug_dir=campaign_debug_dir, 
                                        campaign_filter=campaign_filter, all_campaigns=all_campaigns)
            df_metrics = extractor.run(enzyme_df)

    # Skip final merge since campaign-specific merges already happened during processing
    # This avoids duplicate entries when same enzyme appears in multiple campaigns
    df_final = df_metrics
    LOGGER.info("Using pre-merged campaign data - final dataset has %d rows", len(df_final) if df_final is not None else 0)

    # Rename aa_seq to protein_sequence for consistency
    if df_final is not None and 'aa_seq' in df_final.columns:
        df_final = df_final.rename(columns={'aa_seq': 'protein_sequence'})
        LOGGER.info("Renamed 'aa_seq' column to 'protein_sequence' for consistency")

    df_final.to_csv(args.output, index=False)
    LOGGER.info("Saved %d rows -> %s", len(df_final), args.output)
    
    # Campaign-specific files are already saved during processing above

if __name__ == "__main__":
    main()

