"""enzyme_lineage_extractor.py

Single-file, maintainable CLI tool that pulls an enzyme "family tree" and
associated sequences from one or two PDFs (manuscript + SI) using Google
Gemini (or compatible) LLM.

Navigate by searching for the numbered section headers:

    # === 1. CONFIG & CONSTANTS ===
    # === 2. DOMAIN MODELS ===
    # === 3. LOGGING HELPERS ===
    # === 4. PDF HELPERS ===
    # === 5. LLM (GEMINI) HELPERS ===
    # === 6. LINEAGE EXTRACTION ===
    # === 7. SEQUENCE EXTRACTION ===
    # === 8. VALIDATION & MERGE ===
    # === 9. PIPELINE ORCHESTRATOR ===
    # === 10. CLI ENTRYPOINT ===
"""

# === 1. CONFIG & CONSTANTS ===
from __future__ import annotations
import pandas as pd
import networkx as nx  # light dependency, used only for generation inference

import os
import fitz
import re
import json
import time

# Import universal caption pattern
try:
    from .caption_pattern import get_universal_caption_pattern
except ImportError:
    # Fallback if running as standalone script
    from caption_pattern import get_universal_caption_pattern
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Union, Tuple, Dict, Any

MODEL_NAME: str = "gemini-2.5-flash"
MAX_CHARS: int = 150_000           # Max characters sent to LLM
SEQ_CHUNK: int = 10                # Batch size when prompting for sequences
MAX_RETRIES: int = 4               # LLM retry loop
CACHE_DIR: Path = Path.home() / ".cache" / "enzyme_extractor"

# Ensure cache directory exists
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# === 2. DOMAIN MODELS ===
@dataclass
class Campaign:
    """Representation of a directed evolution campaign."""
    campaign_id: str
    campaign_name: str
    description: str
    model_substrate: Optional[str] = None
    model_product: Optional[str] = None
    substrate_id: Optional[str] = None
    product_id: Optional[str] = None
    data_locations: List[str] = field(default_factory=list)
    reaction_conditions: dict = field(default_factory=dict)
    notes: str = ""

@dataclass
class Variant:
    """Representation of a variant in the evolutionary lineage."""
    variant_id: str
    parent_id: Optional[str]
    mutations: List[str]
    generation: int
    campaign_id: Optional[str] = None  # Links variant to campaign
    notes: str = ""

@dataclass
class SequenceBlock:
    """Protein and/or DNA sequence associated with a variant."""
    variant_id: str
    aa_seq: Optional[str] = None
    dna_seq: Optional[str] = None
    confidence: Optional[float] = None
    truncated: bool = False
    metadata: dict = field(default_factory=dict)

# === 3. LOGGING HELPERS ===

# --- Debug dump helper ----------------------------------------------------
def _dump(text: str | bytes, path: Path | str) -> None:
    """Write `text` / `bytes` to `path`, creating parent dirs as needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    mode = "wb" if isinstance(text, (bytes, bytearray)) else "w"
    with p.open(mode) as fh:
        fh.write(text)

def get_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        handler.setFormatter(logging.Formatter(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

log = get_logger(__name__)

# === 4. PDF HELPERS (incl. caption scraper & figure extraction) ===
try:
    import fitz  # PyMuPDF
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "PyMuPDF is required for PDF parsing. Install with `pip install pymupdf`."
    ) from exc

_DOI_REGEX = re.compile(r"10\.[0-9]{4,9}/[-._;()/:A-Z0-9]+", re.I)

# PDB ID regex - matches 4-character PDB codes (case-insensitive)
_PDB_REGEX = re.compile(r"\b[1-9][A-Za-z0-9]{3}\b")

# Use universal caption pattern
_CAPTION_PREFIX_RE = get_universal_caption_pattern()


def _open_doc(pdf_path: str | Path | bytes):
    if isinstance(pdf_path, (str, Path)):
        return fitz.open(pdf_path)  # type: ignore[arg-type]
    return fitz.open(stream=pdf_path, filetype="pdf")  # type: ignore[arg-type]


def extract_text(pdf_path: str | Path | bytes) -> str:
    """Extract raw text from a PDF file (all blocks)."""

    doc = _open_doc(pdf_path)
    try:
        return "\n".join(page.get_text() for page in doc)
    finally:
        doc.close()


def extract_captions(pdf_path: str | Path | bytes, max_chars: int = MAX_CHARS) -> str:
    """Extract ALL figure/table captions with extensive surrounding context.

    The function scans every text line on every page and keeps lines whose first
    token matches `_CAPTION_PREFIX_RE`. This covers labels such as:
      * Fig. 1, Figure 2A, Figure 2B, Figure 2C (ALL sub-captions)
      * Table S1, Table 4, Scheme 2, Chart 1B
      * Supplementary Fig. S5A, S5B, S5C (ALL variations)
      
    For SI documents, includes extensive context since understanding what each 
    section contains is crucial for accurate location identification.
    """

    doc = _open_doc(pdf_path)
    captions: list[str] = []
    try:
        for page_num, page in enumerate(doc):
            page_dict = page.get_text("dict")
            
            # Get all text blocks on this page for broader context
            page_text_blocks = []
            for block in page_dict.get("blocks", []):
                block_text = ""
                for line in block.get("lines", []):
                    text_line = "".join(span["text"] for span in line.get("spans", []))
                    if text_line.strip():
                        block_text += text_line.strip() + " "
                if block_text.strip():
                    page_text_blocks.append(block_text.strip())
            
            for block_idx, block in enumerate(page_dict.get("blocks", [])):
                # Get all lines in this block
                block_lines = []
                for line in block.get("lines", []):
                    text_line = "".join(span["text"] for span in line.get("spans", []))
                    block_lines.append(text_line.strip())
                
                # Check if any line starts with a caption prefix
                for i, line in enumerate(block_lines):
                    if _CAPTION_PREFIX_RE.match(line):
                        context_parts = []
                        
                        # Add page context for SI documents (more critical there)
                        context_parts.append(f"Page {page_num + 1}")
                        
                        # Add extensive context before the caption (5-7 lines for SI context)
                        context_before = []
                        
                        # First try to get context from current block
                        for k in range(max(0, i-7), i):
                            if k < len(block_lines) and block_lines[k].strip():
                                if not _CAPTION_PREFIX_RE.match(block_lines[k]):
                                    context_before.append(block_lines[k])
                        
                        # If not enough context, look at previous text blocks on the page
                        if len(context_before) < 3 and block_idx > 0:
                            prev_block_text = page_text_blocks[block_idx - 1] if block_idx < len(page_text_blocks) else ""
                            if prev_block_text:
                                # Get last few sentences from previous block
                                sentences = prev_block_text.split('. ')
                                context_before = sentences[-2:] + context_before if len(sentences) > 1 else [prev_block_text] + context_before
                        
                        if context_before:
                            # Include more extensive context for better understanding
                            context_text = " ".join(context_before[-5:])  # Last 5 lines/sentences of context
                            context_parts.append("Context: " + context_text)
                        
                        # Extract the COMPLETE caption including all sub-parts
                        caption_parts = [line]
                        j = i + 1
                        
                        # Continue collecting caption text until we hit a clear break
                        while j < len(block_lines):
                            next_line = block_lines[j]
                            
                            # Stop if we hit an empty line followed by non-caption text
                            if not next_line:
                                # Check if the line after empty is a new caption
                                if j + 1 < len(block_lines) and _CAPTION_PREFIX_RE.match(block_lines[j + 1]):
                                    break
                                # If next non-empty line is not a caption, continue collecting
                                elif j + 1 < len(block_lines):
                                    j += 1
                                    continue
                                else:
                                    break
                            
                            # Stop if we hit a new caption
                            if _CAPTION_PREFIX_RE.match(next_line):
                                break
                            
                            # Include this line as part of the caption
                            caption_parts.append(next_line)
                            j += 1
                        
                        # Join the caption parts
                        full_caption = " ".join(caption_parts)
                        context_parts.append("Caption: " + full_caption)
                        
                        # Add extensive context after the caption (especially important for SI)
                        context_after = []
                        
                        # Look for descriptive text following the caption
                        for k in range(j, min(len(block_lines), j + 10)):  # Look ahead up to 10 lines
                            if k < len(block_lines) and block_lines[k].strip():
                                if not _CAPTION_PREFIX_RE.match(block_lines[k]):
                                    context_after.append(block_lines[k])
                        
                        # If not enough context, look at next text blocks
                        if len(context_after) < 3 and block_idx + 1 < len(page_text_blocks):
                            next_block_text = page_text_blocks[block_idx + 1]
                            if next_block_text:
                                # Get first few sentences from next block
                                sentences = next_block_text.split('. ')
                                context_after.extend(sentences[:3] if len(sentences) > 1 else [next_block_text])
                        
                        if context_after:
                            # Include extensive following context
                            following_text = " ".join(context_after[:7])  # First 7 lines of following context
                            context_parts.append("Following: " + following_text)
                        
                        # For SI documents, add section context if this appears to be a section header
                        if any(keyword in full_caption.lower() for keyword in ['supplementary', 'supporting', 'si ', 's1', 's2', 's3']):
                            context_parts.append("SI_SECTION: This appears to be supplementary material content")
                        
                        # Combine all parts with proper separation
                        full_caption_with_context = " | ".join(context_parts)
                        captions.append(full_caption_with_context)
    finally:
        doc.close()

    joined = "\n".join(captions)
    return joined[:max_chars]


def extract_doi(pdf_path: str | Path | bytes) -> Optional[str]:
    """Attempt to locate a DOI inside the PDF."""

    m = _DOI_REGEX.search(extract_text(pdf_path))
    return m.group(0) if m else None


def extract_pdb_ids(pdf_path: str | Path | bytes) -> List[str]:
    """Extract all PDB IDs from the PDF."""
    text = extract_text(pdf_path)
    
    # Find all potential PDB IDs
    pdb_ids = []
    for match in _PDB_REGEX.finditer(text):
        pdb_id = match.group(0).upper()
        
        # Simple validation - PDB IDs must have at least one letter
        if not any(c.isalpha() for c in pdb_id):
            continue  # Skip all-digit codes like "1021"
            
        # Additional validation - check context for "PDB" mention
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 50)
        context = text[start:end].upper()
        
        # Only include if "PDB" appears in context or it's a known pattern
        if "PDB" in context or "PROTEIN DATA BANK" in context:
            if pdb_id not in pdb_ids:
                pdb_ids.append(pdb_id)
                log.info(f"Found PDB ID: {pdb_id}")
    
    return pdb_ids


def limited_concat(*pdf_paths: str | Path, max_chars: int = MAX_CHARS) -> str:
    """Concatenate **all text** from PDFs, trimmed to `max_chars`."""

    total = 0
    chunks: list[str] = []
    for p in pdf_paths:
        t = extract_text(p)
        if total + len(t) > max_chars:
            t = t[: max_chars - total]
        chunks.append(t)
        total += len(t)
        if total >= max_chars:
            break
    return "\n".join(chunks)


def limited_caption_concat(*pdf_paths: str | Path, max_chars: int = MAX_CHARS) -> str:
    """Concatenate only caption text from PDFs, trimmed to `max_chars`."""

    total = 0
    chunks: list[str] = []
    for p in pdf_paths:
        t = extract_captions(p)
        if total + len(t) > max_chars:
            t = t[: max_chars - total]
        chunks.append(t)
        total += len(t)
        if total >= max_chars:
            break
    return "\n".join(chunks)


def extract_figure(pdf_path: Union[str, Path], figure_id: str, debug_dir: Optional[Union[str, Path]] = None, caption_text: str = "") -> Optional[bytes]:
    """Extract a specific figure from a PDF by finding its caption.
    
    Returns the figure as PNG bytes if found, None otherwise.
    """
    doc = _open_doc(pdf_path)
    figure_bytes = None
    
    try:
        # Use caption text if provided, otherwise use figure_id
        if caption_text:
            # Use first 50 chars of caption for searching (enough to be unique)
            search_text = caption_text[:50].strip()
            log.info(f"Searching for figure using caption: '{search_text}...'")
        else:
            search_text = figure_id.strip()
            log.info(f"Searching for figure using ID: '{search_text}'")
        
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            
            # Check if caption text appears on this page
            if search_text in page_text:
                log.info(f"Found caption on page {page_num + 1}")
                
                # Search for the exact text position
                text_instances = page.search_for(search_text)
                
                if text_instances:
                    # Get the position of the caption
                    caption_rect = text_instances[0]
                
                # Instead of trying to extract individual images, 
                # extract the ENTIRE PAGE as an image
                # This ensures we get the complete figure with all panels
                log.info(f"Extracting entire page {page_num + 1} containing figure {figure_id}")
                
                # Use high resolution for clarity
                mat = fitz.Matrix(3.0, 3.0)  # 3x zoom
                pix = page.get_pixmap(matrix=mat)
                figure_bytes = pix.tobytes("png")
                
                # Save the extracted figure if debug is enabled
                if debug_dir and figure_bytes:
                    debug_path = Path(debug_dir)
                    debug_path.mkdir(parents=True, exist_ok=True)
                    figure_file = debug_path / f"figure_{figure_id.replace(' ', '_')}_{int(time.time())}.png"
                    with open(figure_file, 'wb') as f:
                        f.write(figure_bytes)
                    log.info(f"Saved figure to: {figure_file}")
                
                break  # Found the figure, no need to continue
                
    finally:
        doc.close()
    
    return figure_bytes


def is_figure_reference(location: str) -> bool:
    """Check if a location string refers to a figure."""
    # Check for common figure patterns
    figure_patterns = [
        r'Fig(?:ure)?\.?\s+',      # Fig. 2B, Figure 3
        r'Extended\s+Data\s+Fig',   # Extended Data Fig
        r'ED\s+Fig',                # ED Fig
        r'Scheme\s+',               # Scheme 1
        r'Chart\s+',                # Chart 2
    ]
    
    location_str = str(location).strip()
    for pattern in figure_patterns:
        if re.search(pattern, location_str, re.I):
            return True
    return False

# === 5. LLM (Gemini) HELPERS === ---------------------------------------------
from typing import Tuple, Any

_BACKOFF_BASE = 2.0  # exponential back-off base (seconds)

# -- 5.1  Import whichever SDK is installed -----------------------------------

def _import_gemini_sdk() -> Tuple[str, Any]:
    """Return (flavor, module) where flavor in {"new", "legacy"}."""
    try:
        import google.generativeai as genai  # official SDK >= 1.0
        return "new", genai
    except ImportError:
        try:
            import google_generativeai as genai  # legacy prerelease name
            return "legacy", genai
        except ImportError as exc:
            raise ImportError(
                "Neither 'google-generativeai' (>=1.0) nor 'google_generativeai'\n"
                "is installed.  Run:  pip install --upgrade google-generativeai"
            ) from exc

_SDK_FLAVOR, _genai = _import_gemini_sdk()

# -- 5.2  Model factory --------------------------------------------------------

def get_model():
    """Configure API key and return a `GenerativeModel` instance."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("Set the GEMINI_API_KEY environment variable.")
    _genai.configure(api_key=api_key)
    
    # Create generation config to optimize performance and costs
    generation_config = {
        "temperature": 0.0,  # Deterministic: always pick the most likely token
        "top_p": 1.0,      # Consider all tokens (but temperature=0 will pick the best)
        "top_k": 1,        # Only consider the single most likely token
        "max_output_tokens": 65536,  # Increased to 2x for handling larger lineage tables and sequences
    }
    
    # For Gemini 2.5 Flash, disable thinking tokens to save costs
    # thinking_budget=0 disables thinking, -1 enables dynamic thinking (default)
    # Only add if SDK supports it to maintain compatibility
    try:
        # Test if thinking_budget is supported by making a minimal API call
        test_config = {"thinking_budget": 0, "max_output_tokens": 10}
        test_model = _genai.GenerativeModel(MODEL_NAME, generation_config=test_config)
        # Actually test the API call to see if thinking_budget is supported
        test_response = test_model.generate_content("Return 'OK'")
        # If no error, add thinking_budget to main config
        generation_config["thinking_budget"] = 0
        log.debug("Disabled thinking tokens (thinking_budget=0)")
    except Exception as e:
        # SDK doesn't support thinking_budget, continue without it
        log.debug(f"thinking_budget not supported: {e}")
    
    return _genai.GenerativeModel(MODEL_NAME, generation_config=generation_config)

# === 5.3  Unified call helper ----------------------------------------------

def _extract_text_and_track_tokens(resp) -> str:
    """
    Pull the *first* textual part out of a GenerativeAI response, handling both
    the old prerelease SDK and the >=1.0 SDK. Also tracks token usage.

    Returns an empty string if no textual content is found.
    """
    # Track token usage if available
    try:
        if hasattr(resp, 'usage_metadata'):
            input_tokens = getattr(resp.usage_metadata, 'prompt_token_count', 0)
            output_tokens = getattr(resp.usage_metadata, 'candidates_token_count', 0)
            if input_tokens or output_tokens:
                # Import wrapper token tracking
                try:
                    from .wrapper import add_token_usage
                    add_token_usage('enzyme_lineage_extractor', input_tokens, output_tokens)
                except ImportError:
                    pass  # wrapper not available
    except Exception:
        pass  # token tracking is best-effort

    # 1) Legacy SDK (<= 0.4) - still has nice `.text`
    if getattr(resp, "text", None):
        return resp.text

    # 2) >= 1.0 SDK
    if getattr(resp, "candidates", None):
        cand = resp.candidates[0]

        # 2a) Some beta builds still expose `.text`
        if getattr(cand, "text", None):
            return cand.text

        # 2b) Official path: candidate.content.parts[*].text
        if getattr(cand, "content", None):
            parts = [
                part.text                     # Part objects have .text
                for part in cand.content.parts
                if getattr(part, "text", None)
            ]
            if parts:
                return "".join(parts)

    # 3) As a last resort fall back to str()
    return str(resp)

def _extract_text(resp) -> str:
    """Backward compatibility wrapper for _extract_text_and_track_tokens."""
    try:
        # Check if response has text attribute first
        if hasattr(resp, 'text'):
            return resp.text
        # Fall back to full extraction
        return _extract_text_and_track_tokens(resp)
    except Exception as e:
        # Log the actual error for debugging
        log.error(f"Failed to extract text from response: {e}")
        log.error(f"Response type: {type(resp)}")
        log.error(f"Response attributes: {dir(resp)}")
        # Don't mask the error - let it propagate
        raise


def generate_json_with_retry(
    model,
    prompt: str,
    schema_hint: str | None = None,
    *,
    max_retries: int = MAX_RETRIES,
    debug_dir:str | Path | None = None,
    tag: str = 'gemini',
):
    """
    Call Gemini with retries & exponential back-off, returning parsed JSON.

    Also strips Markdown fences that the model may wrap around its JSON.
    """
    # Log prompt details
    log.info("=== GEMINI API CALL: %s ===", tag.upper())
    log.info("Prompt length: %d characters", len(prompt))
    log.info("First 500 chars of prompt:\n%s\n...(truncated)", prompt[:500])
    
    # Save full prompt to debug directory if provided
    if debug_dir:
        debug_path = Path(debug_dir)
        debug_path.mkdir(parents=True, exist_ok=True)
        prompt_file = debug_path / f"{tag}_prompt_{int(time.time())}.txt"
        with open(prompt_file, 'w') as f:
            f.write(f"=== PROMPT FOR {tag.upper()} ===\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Length: {len(prompt)} characters\n")
            f.write("="*80 + "\n\n")
            f.write(prompt)
        log.info("Full prompt saved to: %s", prompt_file)
    
    fence_re = re.compile(r"```json|```", re.I)
    for attempt in range(1, max_retries + 1):
        try:
            log.info("Calling Gemini API (attempt %d/%d)...", attempt, max_retries)
            resp = model.generate_content(prompt)
            raw = _extract_text(resp).strip()
            
            # Log response
            log.info("Gemini response length: %d characters", len(raw))
            log.info("First 500 chars of response:\n%s\n...(truncated)", raw[:500])
            
            # Save full response to debug directory
            if debug_dir:
                response_file = debug_path / f"{tag}_response_{int(time.time())}.txt"
                with open(response_file, 'w') as f:
                    f.write(f"=== RESPONSE FOR {tag.upper()} ===\n")
                    f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Length: {len(raw)} characters\n")
                    f.write("="*80 + "\n\n")
                    f.write(raw)
                log.info("Full response saved to: %s", response_file)
            
            # Check if response contains header information before JSON
            # This can happen with certain responses
            if raw and not raw.lstrip().startswith(('[', '{')):
                # Look for where JSON actually starts
                lines = raw.split('\n')
                json_start_line = None
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith('[') or stripped.startswith('{') or stripped.lower().startswith('```json'):
                        json_start_line = i
                        break
                
                if json_start_line is not None:
                    # Extract only the JSON part
                    raw = '\n'.join(lines[json_start_line:])
                    log.debug(f"Removed {json_start_line} header lines from response")

            # Remove common Markdown fences
            if raw.startswith("```"):
                raw = fence_re.sub("", raw).strip()
            
            # Try to find JSON in the response
            # First, try to parse as-is
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                # If that fails, look for JSON array or object
                # Find the first '[' or '{' and the matching closing bracket
                json_start = -1
                json_end = -1
                bracket_stack = []
                in_string = False
                escape_next = False
                
                for i, char in enumerate(raw):
                    if escape_next:
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        continue
                        
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        continue
                    
                    if in_string:
                        continue
                    
                    if char in '[{':
                        if json_start == -1:
                            json_start = i
                        bracket_stack.append(char)
                    elif char in ']}':
                        if bracket_stack:
                            opening = bracket_stack.pop()
                            if (opening == '[' and char == ']') or (opening == '{' and char == '}'):
                                if not bracket_stack:  # Found complete JSON
                                    json_end = i + 1
                                    break
                
                if json_start >= 0 and json_end > json_start:
                    # Extract the JSON portion
                    json_str = raw[json_start:json_end]
                    parsed = json.loads(json_str)
                else:
                    # Look for simple [] in the response
                    if '[]' in raw:
                        parsed = []
                    else:
                        # No JSON structure found, re-raise the original error
                        raise json.JSONDecodeError("No JSON structure found in response", raw, 0)
            log.info("Successfully parsed JSON response")
            return parsed
        except Exception as exc:                                 # broad except OK here
            log.warning(
                "Gemini call failed (attempt %d/%d): %s",
                attempt, max_retries, exc,
            )
            if attempt == max_retries:
                raise
            time.sleep(_BACKOFF_BASE ** attempt)

def generate_json_with_retry_multimodal(
    model,
    content_parts: List[Any],
    schema_hint: str | None = None,
    *,
    max_retries: int = MAX_RETRIES,
    debug_dir: str | Path | None = None,
    tag: str = 'gemini_multimodal',
):
    """
    Call Gemini multimodal API with retries & exponential back-off, returning parsed JSON.
    content_parts should be a list containing prompt text and PDF bytes.
    """
    # Extract prompt text for logging (first text element)
    prompt_text = ""
    for part in content_parts:
        if isinstance(part, str):
            prompt_text = part
            break
    
    # Log prompt details
    log.info("=== GEMINI MULTIMODAL API CALL: %s ===", tag.upper())
    log.info("Prompt length: %d characters", len(prompt_text))
    log.info("Number of content parts: %d", len(content_parts))
    log.info("First 500 chars of prompt:\n%s\n...(truncated)", prompt_text[:500])
    
    # Save full prompt to debug directory if provided
    if debug_dir:
        debug_path = Path(debug_dir)
        debug_path.mkdir(parents=True, exist_ok=True)
        prompt_file = debug_path / f"{tag}_prompt_{int(time.time())}.txt"
        with open(prompt_file, 'w') as f:
            f.write(f"=== MULTIMODAL PROMPT FOR {tag.upper()} ===\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Mode: FULL PDFs\n")
            f.write(f"Number of parts: {len(content_parts)}\n")
            f.write("="*80 + "\n\n")
            f.write(prompt_text)
        log.info("Full prompt saved to: %s", prompt_file)
    
    fence_re = re.compile(r"```json|```", re.I)
    for attempt in range(1, max_retries + 1):
        try:
            log.info("Calling Gemini multimodal API (attempt %d/%d)...", attempt, max_retries)
            resp = model.generate_content(content_parts)
            raw = _extract_text(resp).strip()
            
            # Log response
            log.info("Gemini multimodal response length: %d characters", len(raw))
            log.info("First 500 chars of response:\n%s\n...(truncated)", raw[:500])
            
            # Save full response to debug directory
            if debug_dir:
                response_file = debug_path / f"{tag}_response_{int(time.time())}.txt"
                with open(response_file, 'w') as f:
                    f.write(f"=== MULTIMODAL RESPONSE FOR {tag.upper()} ===\n")
                    f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Length: {len(raw)} characters\n")
                    f.write("="*80 + "\n\n")
                    f.write(raw)
                log.info("Full response saved to: %s", response_file)
            
            # Save original for error reporting
            original_raw = raw
            
            # Remove common Markdown fences
            if raw.startswith("```"):
                raw = fence_re.sub("", raw).strip()
            
            # Try to find JSON in the response (same logic as regular version)
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                # Find JSON structure
                json_start = -1
                json_end = -1
                bracket_stack = []
                in_string = False
                escape_next = False
                
                for i, char in enumerate(raw):
                    if escape_next:
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        continue
                        
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        continue
                    
                    if in_string:
                        continue
                    
                    if char in '[{':
                        if json_start == -1:
                            json_start = i
                        bracket_stack.append(char)
                    elif char in ']}':
                        if bracket_stack:
                            opening = bracket_stack.pop()
                            if (opening == '[' and char == ']') or (opening == '{' and char == '}'):
                                if not bracket_stack:  # Found complete JSON
                                    json_end = i + 1
                                    break
                
                if json_start >= 0 and json_end > json_start:
                    json_str = raw[json_start:json_end]
                    parsed = json.loads(json_str)
                else:
                    if '[]' in raw:
                        parsed = []
                    else:
                        # Provide more context in error message using original response
                        preview = original_raw[:200] + "..." if len(original_raw) > 200 else original_raw
                        error_msg = f"No JSON structure found in response. Response preview: {repr(preview)}"
                        log.error(error_msg)
                        log.error(f"Raw after processing: {repr(raw[:200]) if raw else 'EMPTY'}")
                        raise json.JSONDecodeError(error_msg, original_raw, 0)
            
            log.info("Successfully parsed JSON response from multimodal API")
            return parsed
        except Exception as exc:
            log.warning(
                "Gemini multimodal call failed (attempt %d/%d): %s",
                attempt, max_retries, exc,
            )
            if attempt == max_retries:
                raise
            time.sleep(_BACKOFF_BASE ** attempt)
# -------------------------------------------------------------------- end 5 ---


# === 6. LINEAGE EXTRACTION (WITH CAMPAIGN SUPPORT) ===
"""
Variant lineage extractor with campaign identification.

Asks Gemini to produce a JSON representation of the evolutionary lineage of
enzyme variants described in a manuscript.  The heavy lifting is done by the
LLM; this section crafts robust prompts, parses the reply, validates it, and
exposes a convenient high-level `get_lineage()` helper for the pipeline.

June 2025: updated for Google Generative AI SDK >= 1.0 and added rich debug
hooks (`--debug-dir` dumps prompts, replies, and raw captions).

December 2025: Added campaign identification to support multiple directed
evolution campaigns within a single paper.
"""

from pathlib import Path
from typing import List, Dict, Any

# ---- 6.0  Campaign identification prompts -----------------------------------

_CAMPAIGN_IDENTIFICATION_PROMPT = """
Identify directed evolution LINEAGE campaigns in this manuscript provided as PDF(s).

A campaign is a multi-round directed evolution effort that creates a FAMILY of variants through iterative cycles.

ONLY INCLUDE MAIN CAMPAIGNS:
- NEW directed evolution performed in THIS study ("we evolved", "we performed X rounds", "directed evolution yielded")
- Multiple rounds/generations of evolution creating variant families (e.g., "8 rounds", "L1→L2→L3→L4")
- Previously evolved lineages ONLY if they are the PRIMARY FOCUS and comprehensively characterized in THIS paper

DO NOT INCLUDE:
- Studies on individual variants without multi-generational lineage
- Simple characterization of a few variants
- Background mentions of previous campaigns
- Single-point mutations or saturation mutagenesis without evolution cycles
- Variants mentioned only for comparison

IMPORTANT: Be SELECTIVE. Only return campaigns with clear multi-round evolution creating variant families.

FALLBACK RULE: If NO campaigns exist (empty array), THEN and ONLY THEN include systematic variant studies with parent-child relationships.

Key phrases: "rounds of directed evolution", "iterative evolution", "evolutionary lineage", "generations", "we evolved"

Return a JSON array of campaigns:
[
  {{
    "campaign_id": "descriptive_unique_id_that_will_be_used_as_context",
    "campaign_name": "descriptive name",
    "description": "what THIS STUDY evolved for",
    "model_substrate": "substrate name/id",
    "model_product": "product name/id", 
    "substrate_id": "id from paper (e.g., 1a)",
    "product_id": "id from paper (e.g., 2a)",
    "data_locations": ["Table S1", "Figure 1"],
    "lineage_hint": "enzyme name pattern",
    "notes": "evidence this was evolved in THIS study"
  }}
]
""".strip()

_CAMPAIGN_BEST_LOCATION_PROMPT = """
Given this specific campaign and the available data locations, select the BEST location to extract the complete lineage data for this campaign.

Campaign:
- ID: {campaign_id}
- Name: {campaign_name}
- Description: {description}
- Lineage identifiers: {identifiers}

Available locations with context:
{locations_with_context}

Select the location that most likely contains the COMPLETE lineage data (all variants, mutations, and parent relationships) for THIS SPECIFIC campaign.

Consider:
1. Tables are usually more structured and complete than figures
2. Look for locations that mention this campaign's specific identifiers or enzyme names
3. Some locations may contain data for multiple campaigns - that's fine, we can filter later
4. Prioritize completeness over visual clarity

Return a JSON object with:
{{"location": "selected location identifier", "confidence": 0-100, "reason": "explanation"}}
""".strip()

# ---- 6.1  Prompt templates -------------------------------------------------

_LINEAGE_LOC_PROMPT = """
You are an expert reader of protein engineering manuscripts.
{campaign_context}
Given the attached PDF documents (manuscript and/or supplementary information), list up to {max_results} *locations* (figure/table IDs
or section headings) that you would review first to find the COMPLETE evolutionary 
lineage of enzyme variants (i.e. which variant came from which parent and what 
mutations were introduced){campaign_specific}. Pay attention to the provided context after the caption
ensure the location you return are actually lineage location with variants and mutations.

IMPORTANT SCORING CRITERIA:
- Locations that explicitly mention "lineage" should be scored MUCH HIGHER (90-100)
- Locations mentioning "evolutionary tree", "phylogenetic", "genealogy", or "ancestry" should also score high (85-95)
- Locations that only mention "variants" without lineage context should score lower (60-80)
- Generic tables of variants without parent-child relationships should score lowest (40-60)

Respond with a JSON array of objects, each containing:
- "location": the figure/table identifier EXACTLY as it appears in the caption (e.g. "Table S1", "Figure 2B", "Table 1", "Figure 3")
- "type": one of "table", "figure", "section"  
- "confidence": your confidence score (0-100) that this location contains lineage data (PRIORITIZE "lineage" mentions!)
- "reason": brief explanation of why this location likely contains lineage
- "document": one of "manuscript" or "supplementary" - indicate whether this is in the main manuscript or supplementary information
- "caption": the FULL caption text (include at least the first 200-300 characters of the caption to enable fuzzy matching)
{campaign_field}
CRITICAL INSTRUCTIONS:
1. Return "location" EXACTLY as the first reference identifier appears in the actual caption text
   - Copy the exact characters including all punctuation (periods, colons, pipes, etc.) up to the first space after the identifier
   - Do NOT modify, standardize, or interpret the location - return it verbatim from the document
2. Include the FULL caption text in the "caption" field to enable fuzzy matching when extracting
   - This should be the complete caption as it appears in the document
   - Include at least 200-300 characters to ensure unique matching
3. For each location, specify whether it's in the main manuscript or supplementary information (SI):
   - Items like "Table S1", "Figure S2", etc. are typically in the SI
   - Items like "Table 1", "Figure 2", etc. are typically in the main manuscript
   - If uncertain, use context clues from the text

Order by confidence score (highest first), with special priority for:
1. Tables/figures explicitly mentioning "lineage" or "evolutionary tree" (score 90-100)
2. Tables showing complete parent-child relationships with mutations (score 80-95)
3. Figures showing evolutionary/phylogenetic trees (score 75-90)
4. Tables listing variants with parent information (score 70-85)
5. Generic variant tables without clear lineage information (score 40-70)

Don't include oligonucleotide results or result from only one round.

Example output:
[
  {{"location": "Table S1.", "type": "table", "confidence": 98, "reason": "Complete enzyme lineage table with parent-child relationships", "document": "supplementary", "caption": "Table S1. Complete lineage of enzyme variants showing the evolutionary progression from wild-type through eight rounds of directed evolution. Each variant is listed with its parent and accumulated mutations..."{campaign_example}}},
  {{"location": "Figure 2B", "type": "figure", "confidence": 92, "reason": "Evolutionary tree explicitly showing lineage", "document": "manuscript", "caption": "Figure 2B Evolutionary lineage tree depicting the complete genealogy of engineered variants. Branches show parent-child relationships with mutations annotated..."{campaign_example}}},
  {{"location": "Table 2", "type": "table", "confidence": 75, "reason": "Variant table with parent information", "document": "manuscript", "caption": "Table 2. Summary of enzyme variants generated in this study. Parent templates and mutations are indicated for each variant..."{campaign_example}}}
]
""".strip()

_LINEAGE_SCHEMA_HINT = """
{
  "variants": [
    {
      "variant_id": "string",
      "parent_id": "string | null",
      "mutations": ["string"],
      "generation": "int",
      "campaign_id": "string (optional)",
      "notes": "string (optional)"
    }
  ]
}
""".strip()

_LINEAGE_EXTRACT_PROMPT = """
You are analyzing a protein-engineering manuscript provided as PDF(s).
Your task is to output the **complete evolutionary lineage** as JSON conforming
exactly to the schema provided below.

{campaign_context}

Schema:
```json
{schema}
```

Guidelines:
  * Include every named variant that appears in the lineage (WT, libraries,
    hits, final variant, etc.).
  * If a variant appears multiple times, keep the earliest generation.
  * `mutations` must be a list of human-readable point mutations *relative to
    its immediate parent* (e.g. ["L34V", "S152G"]). If no mutations are listed,
    use an empty list.
  * Generation = 0 for the starting template (WT or first variant supplied by
    the authors). Increment by 1 for each subsequent round.
  * If you are uncertain about any field, add an explanatory string to `notes`.
  * IMPORTANT: Only include variants that belong to the campaign context provided above.

⚠️ CRITICAL - CHARACTER RECOGNITION: ⚠️
Be EXTREMELY careful when reading variant names and mutations:
- Do NOT confuse the letter "O" with the number "0" (zero)
- Do NOT confuse the letter "l" (lowercase L) with the number "1" (one)
- Do NOT confuse the letter "I" (uppercase i) with the number "1" (one)
- Do NOT confuse the letter "S" with the number "5"
- Do NOT confuse the letter "G" with the number "6"
- Do NOT confuse the letter "Z" with the number "2"
- Look carefully at the context to determine if a character is a letter or number
- Mutation positions are ALWAYS numbers (e.g., A100V not AlOOV)
- Amino acids are ALWAYS letters (e.g., L34V not 134V)

Return **ONLY** minified JSON, no markdown fences, no commentary.
""".strip()

_LINEAGE_FIGURE_PROMPT = """
You are looking at a figure from a protein-engineering manuscript that shows
the evolutionary lineage of enzyme variants.

{campaign_context}

Your task is to output the **complete evolutionary lineage** as JSON conforming
exactly to the schema provided below.

Schema:
```json
{schema}
```

Guidelines:
  * Include every named variant that appears in the lineage diagram/tree
  * Extract parent-child relationships from the visual connections (arrows, lines, etc.)
  * `mutations` must be a list of human-readable point mutations *relative to
    its immediate parent* (e.g. ["L34V", "S152G"]) if shown
  * Generation = 0 for the starting template (WT or first variant). Increment by 1 
    for each subsequent round/generation shown in the figure
  * If you are uncertain about any field, add an explanatory string to `notes`
  * IMPORTANT: Only include variants that belong to the campaign context provided above.

⚠️ CRITICAL - CHARACTER RECOGNITION IN FIGURES: ⚠️
Be EXTREMELY careful when reading text in figures:
- Do NOT confuse the letter "O" with the number "0" (zero)
- Do NOT confuse the letter "l" (lowercase L) with the number "1" (one)
- Do NOT confuse the letter "I" (uppercase i) with the number "1" (one)
- Do NOT confuse the letter "S" with the number "5"
- Do NOT confuse the letter "G" with the number "6" 
- Do NOT confuse the letter "Z" with the number "2"
- Figures may have lower resolution - zoom in mentally to distinguish characters
- Mutation positions are ALWAYS numbers (e.g., A100V not AlOOV)
- Amino acids are ALWAYS letters (e.g., L34V not 134V)

Return **ONLY** minified JSON, no markdown fences, no commentary.
""".strip()

# ---- 6.2  Helper functions -------------------------------------------------

def identify_campaigns(
    pdf_paths: List[Path],
    model,
    *,
    debug_dir: str | Path | None = None,
) -> List[Campaign]:
    """Identify distinct directed evolution campaigns in the manuscript using multimodal API."""
    # Create prompt without the text placeholder
    prompt = _CAMPAIGN_IDENTIFICATION_PROMPT.replace("{text}", "")
    
    # Prepare multimodal content with PDFs
    content_parts = [prompt]
    
    # Add PDFs to the multimodal request
    for pdf_path in pdf_paths:
        if pdf_path and pdf_path.exists():
            doc_type = "Manuscript" if "si" not in str(pdf_path).lower() else "Supporting Information"
            log.info(f"Adding {doc_type} PDF to multimodal request for campaign identification")
            
            try:
                pdf_bytes = pdf_path.read_bytes()
                # Create a blob dict for the PDF content
                pdf_blob = {
                    "mime_type": "application/pdf",
                    "data": pdf_bytes
                }
                content_parts.append(f"\n\n[{doc_type} PDF]")
                content_parts.append(pdf_blob)
            except Exception as e:
                log.warning(f"Failed to read PDF {pdf_path}: {e}")
    
    campaigns_data: List[dict] = []
    try:
        campaigns_data = generate_json_with_retry_multimodal(
            model,
            content_parts,
            schema_hint=None,
            debug_dir=debug_dir,
            tag="campaigns",
        )
    except Exception as exc:
        log.warning("identify_campaigns(): %s", exc)
    
    # Convert to Campaign objects
    campaigns = []
    for data in campaigns_data:
        try:
            campaign = Campaign(
                campaign_id=data.get("campaign_id", ""),
                campaign_name=data.get("campaign_name", ""),
                description=data.get("description", ""),
                model_substrate=data.get("model_substrate"),
                model_product=data.get("model_product"),
                substrate_id=data.get("substrate_id"),
                product_id=data.get("product_id"),
                data_locations=data.get("data_locations", []),
                reaction_conditions=data.get("reaction_conditions", {}),
                notes=data.get("notes", "")
            )
            campaigns.append(campaign)
            log.info(f"Identified campaign: {campaign.campaign_name} ({campaign.campaign_id})")
        except Exception as exc:
            log.warning(f"Failed to parse campaign data: {exc}")
    
    return campaigns

def identify_evolution_locations(
    text: str,
    model,
    *,
    max_results: int = 5,
    debug_dir: str | Path | None = None,
    campaigns: Optional[List[Campaign]] = None,
    pdf_paths: Optional[List[Path]] = None,
) -> List[dict]:
    """Ask Gemini where in the paper the lineage is probably described using PDF uploads."""
    # Build campaign context for the prompt
    campaign_context = ""
    if campaigns:
        campaign_lines = []
        for camp in campaigns:
            campaign_lines.append(f"- Campaign ID: {camp.campaign_id}")
            campaign_lines.append(f"  Name: {camp.campaign_name}")
            campaign_lines.append(f"  Description: {camp.description}")
            if camp.model_substrate:
                campaign_lines.append(f"  Substrate: {camp.model_substrate}")
            if camp.model_product:
                campaign_lines.append(f"  Product: {camp.model_product}")
        campaign_context = "\n".join(campaign_lines)
    
    # Prepare prompt
    prompt = _LINEAGE_LOC_PROMPT.format(
        campaign_context=campaign_context or "No specific campaigns identified",
        max_results=max_results,
        campaign_specific="",
        campaign_field="",
        campaign_example=""
    )
    
    # Prepare multimodal content with PDFs
    content_parts = [prompt]
    
    # Add PDFs to the multimodal request
    if pdf_paths:
        for pdf_path in pdf_paths:
            if pdf_path and pdf_path.exists():
                doc_type = "Manuscript" if "si" not in str(pdf_path).lower() else "Supporting Information"
                log.info(f"Adding {doc_type} PDF to multimodal request for location identification")
                
                try:
                    pdf_bytes = pdf_path.read_bytes()
                    # Create a blob dict for the PDF content
                    pdf_blob = {
                        "mime_type": "application/pdf",
                        "data": pdf_bytes
                    }
                    content_parts.append(f"\n\n[{doc_type} PDF]")
                    content_parts.append(pdf_blob)
                except Exception as e:
                    log.warning(f"Failed to read PDF {pdf_path}: {e}")
    
    # Call Gemini with PDFs
    locs = []
    try:
        locs = generate_json_with_retry_multimodal(
            model,
            content_parts,
            debug_dir=debug_dir,
            tag="locate_with_pdf",
        )
    except Exception as exc:
        log.warning("identify_evolution_locations(): %s", exc)
    
    return locs if isinstance(locs, list) else []



def _parse_variants(data: Dict[str, Any], campaign_id: Optional[str] = None) -> List[Variant]:
    """Convert raw JSON to a list[Variant] with basic validation."""
    if isinstance(data, list):
        # Direct array of variants
        variants_json = data
    elif isinstance(data, dict):
        # Object with "variants" key
        variants_json = data.get("variants", [])
    else:
        variants_json = []
    parsed: List[Variant] = []
    for item in variants_json:
        try:
            variant_id = str(item["variant_id"]).strip()
            parent_id = item.get("parent_id")
            parent_id = str(parent_id).strip() if parent_id else None
            mutations = [str(m).strip() for m in item.get("mutations", [])]
            generation = int(item.get("generation", 0))
            notes = str(item.get("notes", "")).strip()
            
            # Use campaign_id from item if present, otherwise use the passed campaign_id, 
            # otherwise default to "default"
            variant_campaign_id = item.get("campaign_id") or campaign_id or "default"
            
            parsed.append(
                Variant(
                    variant_id=variant_id,
                    parent_id=parent_id,
                    mutations=mutations,
                    generation=generation,
                    campaign_id=variant_campaign_id,
                    notes=notes,
                )
            )
        except Exception as exc:  # pragma: no cover
            log.debug("Skipping malformed variant entry %s: %s", item, exc)
    return parsed



def extract_complete_lineage(
    text: str,
    model,
    *,
    debug_dir: str | Path | None = None,
    campaign_id: Optional[str] = None,
    campaign_info: Optional[Campaign] = None,
    pdf_paths: Optional[List[Path]] = None,
    location_hint: Optional[str] = None,
) -> List[Variant]:
    """Prompt Gemini for the full lineage and return a list[Variant].
    
    Note: 'text' parameter is kept for compatibility but will be ignored if pdf_paths is provided.
    """
    # Build campaign context
    campaign_context = ""
    if campaign_info:
        campaign_context = f"""
CAMPAIGN CONTEXT:
You are extracting the lineage for the following campaign:
- Campaign ID: {campaign_info.campaign_id}
- Campaign: {campaign_info.campaign_name}
- Description: {campaign_info.description}
- Model reaction: {campaign_info.substrate_id} → {campaign_info.product_id}
- Lineage hint: Variants containing "{campaign_info.notes}" belong to this campaign

IMPORTANT: 
1. Only extract variants that belong to this specific campaign.
2. Include "campaign_id": "{campaign_info.campaign_id}" for each variant in your response.
3. Use the lineage hint pattern above to identify which variants belong to this campaign.
4. Include parent variants only if they are direct ancestors in this campaign's lineage.
"""
    
    # Add location context if provided
    location_context = ""
    if location_hint:
        location_context = f"""

LOCATION HINT:
{location_hint}

This is a hint about where to focus your attention in the document, but extract all relevant variants from the full text provided.
"""
    
    # Extract table of contents from PDFs if available  
    toc_text = ""
    if pdf_paths:
        toc_sections = []
        for pdf_path in pdf_paths:
            # Extract first few pages looking for TOC
            doc = _open_doc(pdf_path)
            try:
                for page_num in range(min(5, len(doc))):
                    page_text = doc[page_num].get_text()
                    if any(indicator in page_text.lower() for indicator in ['table of contents', 'contents', 'summary']):
                        # Found TOC page
                        lines = page_text.split('\n')
                        toc_lines = []
                        for line in lines:
                            line = line.strip()
                            # TOC entries typically have page numbers
                            if (re.search(r'\.{2,}\s*S?\d+\s*$', line) or
                                re.search(r'\s{2,}S?\d+\s*$', line) or
                                re.match(r'^\d+\.\s+\w+', line)):
                                toc_lines.append(line)
                        if toc_lines:
                            pdf_name = pdf_path.name
                            toc_sections.append(f"\n--- Table of Contents from {pdf_name} ---\n" + '\n'.join(toc_lines))
                            break
            finally:
                doc.close()
        
        if toc_sections:
            toc_text = "\n\nTABLE OF CONTENTS SECTIONS:" + ''.join(toc_sections) + "\n\n"
    
    # Combine campaign and location context
    full_context = campaign_context + location_context
    
    # Add TOC text to the context if available
    if toc_text:
        full_context = full_context + toc_text
    
    prompt = _LINEAGE_EXTRACT_PROMPT.format(
        campaign_context=full_context,
        schema=_LINEAGE_SCHEMA_HINT,
    )
    
    # Prepare multimodal content with PDFs
    content_parts = [prompt]
    
    # Add PDFs to the multimodal request if available
    if pdf_paths:
        for pdf_path in pdf_paths:
            if pdf_path and pdf_path.exists():
                doc_type = "Manuscript" if "si" not in str(pdf_path).lower() else "Supporting Information"
                log.info(f"Adding {doc_type} PDF to multimodal request for lineage extraction")
                
                try:
                    pdf_bytes = pdf_path.read_bytes()
                    # Create a blob dict for the PDF content
                    pdf_blob = {
                        "mime_type": "application/pdf",
                        "data": pdf_bytes
                    }
                    content_parts.append(f"\n\n[{doc_type} PDF]")
                    content_parts.append(pdf_blob)
                except Exception as e:
                    log.warning(f"Failed to read PDF {pdf_path}: {e}")
    else:
        # Fallback to text-based extraction if no PDFs provided
        log.warning("No PDFs provided for lineage extraction, falling back to text-based extraction")
        content_parts = [prompt + f"\n\nTEXT:\n```\n{text[:MAX_CHARS]}\n```"]
    
    # Call multimodal API
    raw = generate_json_with_retry_multimodal(
        model,
        content_parts,
        schema_hint=_LINEAGE_SCHEMA_HINT,
        debug_dir=debug_dir,
        tag="lineage",
    ) if len(content_parts) > 1 else generate_json_with_retry(
        model,
        content_parts[0],
        schema_hint=_LINEAGE_SCHEMA_HINT,
        debug_dir=debug_dir,
        tag="lineage",
    )
    variants = _parse_variants(raw, campaign_id=campaign_id)
    log.info("Extracted %d lineage entries", len(variants))
    return variants


def extract_lineage_from_figure(
    figure_bytes: bytes,
    model,
    *,
    debug_dir: str | Path | None = None,
    campaign_id: Optional[str] = None,
    campaign_info: Optional[Campaign] = None,
) -> List[Variant]:
    """Extract lineage from a figure image using Gemini's vision capabilities."""
    # Build campaign context
    campaign_context = ""
    if campaign_info:
        campaign_context = f"""
CAMPAIGN CONTEXT:
You are extracting the lineage for the following campaign:
- Campaign: {campaign_info.campaign_name}
- Description: {campaign_info.description}
- Model reaction: {campaign_info.substrate_id} → {campaign_info.product_id}
- Lineage hint: Variants containing "{campaign_info.notes}" belong to this campaign

IMPORTANT: Only extract variants that belong to this specific campaign.
"""
    
    prompt = _LINEAGE_FIGURE_PROMPT.format(
        campaign_context=campaign_context,
        schema=_LINEAGE_SCHEMA_HINT
    )
    
    # Log prompt details
    log.info("=== GEMINI VISION API CALL: FIGURE_LINEAGE ===")
    log.info("Prompt length: %d characters", len(prompt))
    log.info("Image size: %d bytes", len(figure_bytes))
    log.info("First 500 chars of prompt:\n%s\n...(truncated)", prompt[:500])
    
    # Save prompt and image to debug directory if provided
    if debug_dir:
        debug_path = Path(debug_dir)
        debug_path.mkdir(parents=True, exist_ok=True)
        
        # Save prompt
        prompt_file = debug_path / f"figure_lineage_prompt_{int(time.time())}.txt"
        _dump(f"=== PROMPT FOR FIGURE_LINEAGE ===\nTimestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\nLength: {len(prompt)} characters\nImage size: {len(figure_bytes)} bytes\n{'='*80}\n\n{prompt}",
              prompt_file)
        log.info("Full prompt saved to: %s", prompt_file)
        
        # Save image
        image_file = debug_path / f"figure_lineage_image_{int(time.time())}.png"
        _dump(figure_bytes, image_file)
        log.info("Figure image saved to: %s", image_file)
    
    # For Gemini vision API, we need to pass the image differently
    # This will depend on the specific SDK version being used
    try:
        # Create a multimodal prompt with the image
        import PIL.Image
        import io
        
        # Convert bytes to PIL Image
        image = PIL.Image.open(io.BytesIO(figure_bytes))
        
        log.info("Calling Gemini Vision API...")
        # Generate content with image
        response = model.generate_content([prompt, image])
        raw_text = _extract_text(response).strip()
        
        # Log response
        log.info("Gemini figure analysis response length: %d characters", len(raw_text))
        log.info("First 500 chars of response:\n%s\n...(truncated)", raw_text[:500])
        
        # Save response to debug directory if provided
        if debug_dir:
            debug_path = Path(debug_dir)
            debug_path.mkdir(parents=True, exist_ok=True)
            response_file = debug_path / f"figure_lineage_response_{int(time.time())}.txt"
            with open(response_file, 'w') as f:
                f.write(f"=== RESPONSE FOR FIGURE LINEAGE ===\n")
                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Length: {len(raw_text)} characters\n")
                f.write("="*80 + "\n\n")
                f.write(raw_text)
            log.info("Full response saved to: %s", response_file)
        
        # Check if response contains header information before JSON
        # This can happen with certain responses
        if raw_text and not raw_text.lstrip().startswith(('[', '{')):
            # Look for where JSON actually starts
            lines = raw_text.split('\n')
            json_start_line = None
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('[') or stripped.startswith('{') or stripped.lower().startswith('```json'):
                    json_start_line = i
                    break
            
            if json_start_line is not None:
                # Extract only the JSON part
                raw_text = '\n'.join(lines[json_start_line:])
                log.debug(f"Removed {json_start_line} header lines from response")
        
        # Parse JSON from response
        fence_re = re.compile(r"```json|```", re.I)
        if raw_text.startswith("```"):
            raw_text = fence_re.sub("", raw_text).strip()
        
        raw = json.loads(raw_text)
        
        # Handle both array and object formats
        if isinstance(raw, list):
            # Direct array format - convert to expected format
            variants_data = {"variants": raw}
        else:
            # Already in object format
            variants_data = raw
            
        variants = _parse_variants(variants_data, campaign_id=campaign_id)
        log.info("Extracted %d lineage entries from figure", len(variants))
        return variants
        
    except Exception as exc:
        log.warning("Failed to extract lineage from figure: %s", exc)
        return []


# ---- 6.3  Helper for location-based extraction -----------------------------

def _is_toc_entry(text: str, position: int, pattern: str) -> bool:
    """Check if a found pattern is likely a table of contents entry."""
    # Find the line containing this position
    line_start = text.rfind('\n', 0, position)
    line_end = text.find('\n', position)
    
    if line_start == -1:
        line_start = 0
    else:
        line_start += 1
        
    if line_end == -1:
        line_end = len(text)
        
    line = text[line_start:line_end]
    
    # TOC indicators:
    # 1. Line contains dots (...) followed by page number
    # 2. Line ends with just a page number
    # 3. Line has "Table S12:" or similar followed by title and page
    # 4. Pattern appears at start of line followed by description and page number
    if ('...' in line or 
        re.search(r'\.\s*\d+\s*$', line) or 
        re.search(r':\s*[^:]+\s+\d+\s*$', line) or
        (line.strip().startswith(pattern) and re.search(r'\s+\d+\s*$', line))):
        return True
        
    # Check if this is in a contents/TOC section
    # Look backwards up to 1000 chars for "Contents" or "Table of Contents"
    context_start = max(0, position - 1000)
    context = text[context_start:position].lower()
    if 'contents' in context or 'table of contents' in context:
        return True
    
    # Check if we're in the first ~5000 chars of the document (likely TOC area)
    # This helps catch TOC entries that don't have obvious formatting
    if position < 5000:
        # Be more strict for early document positions
        # Check if line looks like a TOC entry (has page number at end)
        if re.search(r'\s+\d+\s*$', line):
            return True
        
    return False


def _extract_location_text(full_text: str, location: str, location_type: str, caption_hint: str = "") -> Optional[str]:
    """Extract text from a specific location in the document."""
    log = logging.getLogger("debase.enzyme_lineage_extractor")
    
    # For tables, try to find table content
    if location_type == 'table':
        # Look for table markers
        patterns = [
            rf'{re.escape(location)}[^\n]*\n((?:.*\n){{0,200}})',  # Table S1\n...
            rf'{re.escape(location)}[^.]*\.[^\n]*\n((?:.*\n){{0,200}})',  # Table S1. Caption...\n...
        ]
        
        for pattern in patterns:
            match = re.search(pattern, full_text, re.IGNORECASE | re.MULTILINE)
            if match:
                start = match.start()
                # Try to capture the full table (up to 15000 chars)
                end = min(start + 15000, len(full_text))
                return full_text[start:end]
    
    # For sections, look for section headers
    elif location_type == 'section':
        # Try to find section header
        patterns = [
            rf'(?:^|\n)\s*{re.escape(location)}[^\n]*\n((?:.*\n){{0,500}})',
            rf'(?:^|\n)\s*[IVX]+\.\s*{re.escape(location)}[^\n]*\n((?:.*\n){{0,500}})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, full_text, re.IGNORECASE | re.MULTILINE)
            if match:
                start = match.start()
                end = min(start + 20000, len(full_text))
                return full_text[start:end]
    
    # For figures, check if location is a figure reference
    elif location_type == 'figure':
        # This shouldn't happen as figures are handled separately
        log.warning(f"Figure location '{location}' passed to text extraction")
        return None
    
    # Generic text search fallback
    # Try to find the location string in the text
    idx = full_text.lower().find(location.lower())
    if idx != -1:
        start = max(0, idx - 500)
        end = min(idx + 10000, len(full_text))
        return full_text[start:end]
    
    log.warning(f"Could not find location '{location}' of type '{location_type}' in text")
    return None



# ---- 6.4  Public API -------------------------------------------------------


def get_lineage(
    caption_text: str,
    full_text: str,
    model,
    *,
    pdf_paths: Optional[List[Path]] = None,
    debug_dir: str | Path | None = None,
    manuscript_text: Optional[str] = None,
    si_text: Optional[str] = None,
) -> Tuple[List[Variant], List[Campaign]]:
    """
    High-level wrapper used by the pipeline.

    1. Identify distinct campaigns in the manuscript.
    2. Use captions to ask Gemini where the lineage is likely described (fast & focused).
    3. Map locations to campaigns.
    4. Extract lineage for each campaign separately.
    5. Return both variants and campaigns.
    """
    # First, identify campaigns in the manuscript
    campaigns = identify_campaigns(pdf_paths, model, debug_dir=debug_dir)
    
    if campaigns:
        log.info(f"Identified {len(campaigns)} distinct campaigns")
        for camp in campaigns:
            log.info(f"  - {camp.campaign_name}: {camp.description}")
    else:
        log.warning("No campaigns identified, creating default campaign for enzyme characterization")
        # Create a default campaign when none are found
        default_campaign = Campaign(
            campaign_id="default_characterization",
            campaign_name="Enzyme Characterization Study",
            description="Default campaign for papers that characterize existing enzyme variants without describing new directed evolution",
            model_substrate="Unknown",
            model_product="Unknown",
            data_locations=["Full manuscript text"]
        )
        campaigns = [default_campaign]
        log.info(f"Created default campaign: {default_campaign.campaign_name}")
    
    all_variants = []
    
    if campaigns:
        log.info("Using campaign-aware location identification")
        
        # Process each campaign separately
        for campaign in campaigns:
            log.info(f"\nProcessing campaign: {campaign.campaign_id} - {campaign.campaign_name}")
            
            # Use identify_evolution_locations with campaign context
            locations = identify_evolution_locations(
                caption_text, 
                model,
                max_results=5,
                debug_dir=debug_dir,
                campaigns=[campaign],  # Pass single campaign for focused search
                pdf_paths=pdf_paths
            )
            
            if not locations:
                log.warning(f"No locations found for campaign {campaign.campaign_id}, trying full text extraction")
                # Fall back to full text extraction
                campaign_variants = extract_complete_lineage(
                    full_text, model, 
                    debug_dir=debug_dir, 
                    campaign_id=campaign.campaign_id,
                    campaign_info=campaign,
                    pdf_paths=pdf_paths
                )
                all_variants.extend(campaign_variants)
                continue
            
            log.info(f"Found {len(locations)} potential locations for campaign {campaign.campaign_id}")
            for loc in locations:
                log.info(f"  - {loc['location']} ({loc['type']}, confidence: {loc['confidence']})")
            
            # Sort locations by confidence and use the highest confidence one
            locations_sorted = sorted(locations, key=lambda x: x.get('confidence', 0), reverse=True)
            log.info(f"Using highest confidence location: {locations_sorted[0]['location']} (confidence: {locations_sorted[0]['confidence']})")
            
            # Use the highest confidence location as primary location
            primary_location = locations_sorted[0]
            
            # Extract location details
            location_str = primary_location.get('location', '')
            location_type = primary_location.get('type', '')
            confidence = primary_location.get('confidence', 0)
            caption_text = primary_location.get('caption', '')
            
            # Create location hint for full text extraction
            location_hint = f"Focus on {location_type} {location_str}"
            if caption_text:
                location_hint += f" with caption: {caption_text[:200]}..."
            
            log.info(f"Using full text extraction with location hint: {location_hint}")
            
            # Always use full text extraction with location hint
            campaign_variants = extract_complete_lineage(
                full_text, model,
                debug_dir=debug_dir,
                campaign_id=campaign.campaign_id,
                campaign_info=campaign,
                pdf_paths=pdf_paths,
                location_hint=location_hint
            )
            
            if campaign_variants:
                log.info(f"Extracted {len(campaign_variants)} variants for campaign {campaign.campaign_id}")
                all_variants.extend(campaign_variants)
            else:
                log.warning(f"No variants extracted for campaign {campaign.campaign_id}")
        
        return all_variants, campaigns
    
    # Original fallback code for when no campaigns are identified
    log.info("Processing campaigns with direct caption and TOC analysis (skipping global location finding)")
    
    # Prepare all captions and TOC with context for campaign-specific selection
    caption_entries = []
    
    # Add table of contents entries if available
    if pdf_paths:
        toc_sections = []
        for pdf_path in pdf_paths:
            # Extract first few pages looking for TOC
            try:
                doc = fitz.open(pdf_path)
                toc_text = ""
                for page_num in range(min(5, doc.page_count)):  # First 5 pages
                    page = doc[page_num]  # Correct PyMuPDF syntax
                    page_text = page.get_text()
                    if any(keyword in page_text.lower() for keyword in ['contents', 'table of contents', 'overview']):
                        toc_text += f"\n--- Page {page_num + 1} TOC ---\n{page_text}\n"
                doc.close()
                if toc_text:
                    toc_sections.append(toc_text)
            except Exception as e:
                log.warning(f"Failed to extract TOC from {pdf_path}: {e}")
            
            if toc_sections:
                caption_entries.append({
                    'type': 'table_of_contents',
                    'location': 'Table of Contents',
                    'context': '\n'.join(toc_sections)[:1000] + "..."
                })
        
        # Parse figure and table captions from caption_text
        # Split by common caption patterns
        caption_patterns = [
            r'(?:^|\n)(?:Figure|Fig\.?)\s*\d+[:\.]',
            r'(?:^|\n)(?:Table|Tab\.?)\s*\d+[:\.]',
            r'(?:^|\n)(?:Scheme|Sch\.?)\s*\d+[:\.]'
        ]
        
        import re
        for pattern in caption_patterns:
            matches = list(re.finditer(pattern, caption_text, re.MULTILINE | re.IGNORECASE))
            for i, match in enumerate(matches):
                start_pos = match.start()
                # Find the end of this caption (start of next caption or end of text)
                if i + 1 < len(matches):
                    end_pos = matches[i + 1].start()
                else:
                    end_pos = min(start_pos + 2000, len(caption_text))  # Max 2000 chars per caption
                
                caption_content = caption_text[start_pos:end_pos].strip()
                if len(caption_content) > 20:  # Skip very short captions
                    # Extract context from full text around this caption
                    context_start = max(0, full_text.find(caption_content[:100]) - 500)
                    context_end = min(len(full_text), context_start + 2000)
                    context = full_text[context_start:context_end]
                    
                    caption_entries.append({
                        'type': 'figure' if 'fig' in pattern.lower() else 'table' if 'tab' in pattern.lower() else 'scheme',
                        'location': caption_content.split('\n')[0][:100] + "..." if len(caption_content.split('\n')[0]) > 100 else caption_content.split('\n')[0],
                        'context': context
                    })
        
        log.info(f"Prepared {len(caption_entries)} caption/TOC entries for campaign-specific analysis")
        
        # If no caption entries found, fall back to full text extraction
        if not caption_entries:
            log.info("No caption entries found, extracting from full text with campaign context")
            for campaign in campaigns:
                log.info(f"Processing campaign: {campaign.campaign_id}")
                campaign_variants = extract_complete_lineage(
                    full_text, model, 
                    debug_dir=debug_dir, 
                    campaign_id=campaign.campaign_id,
                    campaign_info=campaign,
                    pdf_paths=pdf_paths
                )
                all_variants.extend(campaign_variants)
            return all_variants, campaigns
        
        # For each campaign, ask Gemini to select the best location from captions/TOC
        for campaign in campaigns:
            log.info(f"Processing campaign: {campaign.campaign_id}")
            
            # Build locations context string from caption entries
            locations_str = ""
            for i, entry in enumerate(caption_entries):
                location_str = entry['location']
                location_type = entry['type']
                context = entry['context']
                
                locations_str += f"\n{i+1}. {location_str} (Type: {location_type})\n"
                locations_str += f"   Context (first 500 chars):\n   {context[:500]}...\n"
            
            # Ask Gemini to select best location for this campaign
            best_location_prompt = _CAMPAIGN_BEST_LOCATION_PROMPT.format(
                campaign_id=campaign.campaign_id,
                campaign_name=campaign.campaign_name,
                description=campaign.description,
                identifiers=campaign.notes or "No specific identifiers provided",
                locations_with_context=locations_str
            )
            
            primary_location = None
            try:
                # Save prompt to debug if provided
                if debug_dir:
                    debug_path = Path(debug_dir)
                    debug_path.mkdir(parents=True, exist_ok=True)
                    prompt_file = debug_path / f"best_location_{campaign.campaign_id}_{int(time.time())}.txt"
                    _dump(f"=== BEST LOCATION PROMPT ===\nCampaign: {campaign.campaign_id}\n{'='*80}\n\n{best_location_prompt}", prompt_file)
                
                response = model.generate_content(best_location_prompt)
                response_text = _extract_text(response).strip()
                
                # Parse JSON response
                if response_text.startswith("```"):
                    response_text = response_text.split("```")[1].strip()
                    if response_text.startswith("json"):
                        response_text = response_text[4:].strip()
                
                best_loc_data = json.loads(response_text)
                selected_location = best_loc_data.get('location', '')
                confidence = best_loc_data.get('confidence', 0)
                reason = best_loc_data.get('reason', '')
                
                # Save response to debug if provided
                if debug_dir:
                    response_file = debug_path / f"best_location_response_{campaign.campaign_id}_{int(time.time())}.txt"
                    _dump(f"=== BEST LOCATION RESPONSE ===\nCampaign: {campaign.campaign_id}\nSelected: {selected_location}\nConfidence: {confidence}\nReason: {reason}\n{'='*80}", response_file)
                
                log.info(f"Selected location for {campaign.campaign_id}: {selected_location} (confidence: {confidence})")
                
                # Find the actual caption entry
                selected_entry = None
                for entry in caption_entries:
                    if entry['location'] == selected_location:
                        selected_entry = entry
                        break
                
                if not selected_entry:
                    log.warning(f"Could not find selected location '{selected_location}' in caption entries")
                    # Fall back to first entry
                    selected_entry = caption_entries[0] if caption_entries else None
                
                # Convert caption entry to location format for compatibility
                if selected_entry:
                    primary_location = {
                        'location': selected_entry['location'],
                        'type': selected_entry['type'],
                        'confidence': 0.8,  # Default confidence for caption-based selection
                        'reason': f"Selected from {selected_entry['type']} captions"
                    }
                    
            except Exception as e:
                log.warning(f"Failed to select best location for campaign {campaign.campaign_id}: {e}")
                # Fall back to first caption entry
                if caption_entries:
                    primary_location = {
                        'location': caption_entries[0]['location'],
                        'type': caption_entries[0]['type'],
                        'confidence': 0.5,  # Lower confidence for fallback
                        'reason': f"Fallback to first {caption_entries[0]['type']} caption"
                    }
                else:
                    primary_location = None
            
            if not primary_location:
                log.warning(f"No location found for campaign {campaign.campaign_id}")
                continue
            
            # Log location hints for context
            location_str = None
            if isinstance(primary_location, dict):
                location_str = primary_location.get('location', '')
                location_type = primary_location.get('type', '')
                confidence = primary_location.get('confidence', 0)
                reason = primary_location.get('reason', '')
                
                log.info("Primary location hint: %s (%s) - confidence: %d, reason: %s", 
                         location_str, location_type, confidence, reason)
            
            # Always use full text extraction (locations are just hints)
            log.info("Extracting lineage from full text for campaign %s", campaign.campaign_id)
            
            # Extract lineage for this campaign from full text with location hint
            campaign_variants = extract_complete_lineage(
                full_text, model, 
                debug_dir=debug_dir, 
                campaign_id=campaign.campaign_id,
                campaign_info=campaign,
                pdf_paths=pdf_paths,
                location_hint=location_str  # Pass location hint
            )
            all_variants.extend(campaign_variants)
        
        return all_variants, campaigns
    else:
        log.info("Gemini did not identify specific lineage locations")
        variants = extract_complete_lineage(full_text, model, debug_dir=debug_dir, pdf_paths=pdf_paths)
        return variants, campaigns

# === 7. SEQUENCE EXTRACTION === ----------------------------------------------
# Pull every protein and/or DNA sequence for each variant.
#   1. Ask Gemini where sequences live (cheap, quick prompt).
#   2. Ask Gemini to return the sequences in strict JSON.
#   3. Validate and convert to `SequenceBlock` objects.

# --- 7.0  JSON schema hint ----------------------------------------------------
_SEQUENCE_SCHEMA_HINT = """
[
  {
    "variant_id": "string",         // e.g. "IV-G2", "Round4-10"
    "aa_seq":    "string|null",     // uppercase amino acids or null
    "dna_seq":   "string|null"      // uppercase A/C/G/T or null
  }
]
""".strip()

# --- 7.1  Quick scan: where are the sequences? --------------------------------
_SEQ_LOC_PROMPT = """
Find where FULL-LENGTH protein or DNA sequences are located in this document.

PRIORITY: Protein/amino acid sequences are preferred over DNA sequences.

Look for table of contents entries or section listings that mention sequences.
Return a JSON array where each element has:
- "section": the section heading or description EXACTLY as it appears
- "page": the page number (IMPORTANT: Return ONLY the number, e.g., "53" not "p. 53" or "page 53")
- "document": one of "manuscript" or "supplementary" - indicate whether this is in the main manuscript or supplementary information
- "caption": the FULL section heading or table of contents entry (at least 100-200 characters for fuzzy matching)

Focus on:
- Table of contents or entries about "Sequence Information" or "Nucleotide and amino acid sequences"
- For supplementary pages, use "S" prefix (e.g., "S53" not "p. S53")
- Prioritize sections that mention "protein" or "amino acid" sequences

CRITICAL: 
1. Page numbers must be returned as plain numbers or S-prefixed numbers only:
   - Correct: "53", "S12", "147"
   - Wrong: "p. 53", "P. 53", "page 53", "pg 53"
2. For each location, specify whether it's in the main manuscript or supplementary information (SI):
   - Pages with "S" prefix (e.g., "S53") are typically in the SI
   - Regular page numbers (e.g., "53") are typically in the main manuscript
   - Use context clues from the document structure

Return [] if no sequence sections are found.
Absolutely don't include nucleotides or primer sequences, it is better to return nothing then incomplete sequence, use your best judgement.

TEXT (truncated):
```
{chunk}
```
""".strip()

def identify_sequence_locations(text: str, model, *, debug_dir: str | Path | None = None) -> list[dict]:
    """Ask Gemini for promising places to look for sequences."""
    prompt = _SEQ_LOC_PROMPT.format(chunk=text)
    try:
        locs = generate_json_with_retry(model, prompt, debug_dir=debug_dir, tag="seq_locations")
        return locs if isinstance(locs, list) else []
    except Exception as exc:                                              # pylint: disable=broad-except
        log.warning("identify_sequence_locations(): %s", exc)
        return []

# --- 7.2  Page-based extraction helper ---------------------------------------
def _extract_plain_sequence_with_triple_validation(prompt: str, model, context: str = "") -> Optional[str]:
    """Extract plain text sequence using Gemini with 6 attempts, returning most common result.
    
    Args:
        prompt: The prompt to send to Gemini
        model: The Gemini model instance
        context: Additional context for logging (e.g., "validation" or "extraction")
    
    Returns:
        The most common sequence or None if all attempts failed
    """
    sequences = []
    max_attempts = 6
    
    # Try 6 times
    for attempt in range(max_attempts):
        try:
            response = model.generate_content(prompt)
            result = _extract_text(response).strip()
            
            # Parse the result to extract just the sequence
            if result == "VALID":
                sequences.append("VALID")
            elif result == "UNCERTAIN":
                sequences.append("UNCERTAIN")
            elif result.startswith("M") and len(result) > 50:
                # Clean the sequence
                clean_seq = result.upper().replace(" ", "").replace("\n", "")
                if all(c in "ACDEFGHIKLMNPQRSTVWY*" for c in clean_seq):
                    sequences.append(clean_seq)
                else:
                    sequences.append("INVALID")
            else:
                sequences.append("INVALID")
                
            log.info(f"Gemini {context} attempt {attempt + 1}: {len(result) if result.startswith('M') else result}")
            
        except Exception as e:
            log.warning(f"Gemini {context} attempt {attempt + 1} failed: {e}")
            sequences.append("ERROR")
    
    # After all attempts, find most common result
    valid_sequences = [s for s in sequences if s not in ["INVALID", "ERROR"]]
    
    if not valid_sequences:
        log.error(f"All {max_attempts} {context} attempts failed")
        return None
    
    # Count occurrences of each valid sequence
    sequence_counts = {}
    for seq in valid_sequences:
        if seq not in ["VALID", "UNCERTAIN"]:
            # Clean sequence before counting
            seq_clean = seq.replace(" ", "").replace("\n", "")
            sequence_counts[seq_clean] = sequence_counts.get(seq_clean, 0) + 1
    
    # Return the most common sequence
    if sequence_counts:
        most_common = max(sequence_counts.items(), key=lambda x: x[1])
        log.info(f"Gemini {context} most common: sequence appeared {most_common[1]}/{max_attempts} times")
        return most_common[0]
    
    log.warning(f"Gemini {context} no valid sequences after {max_attempts} attempts")
    return None



def _extract_text_from_page(pdf_paths: List[Path], page_num: Union[str, int], skip_si_toc: bool = True) -> str:
    """Extract text from a specific page number in the PDFs.
    
    Args:
        pdf_paths: List of PDF paths
        page_num: Page number (can be "S1", "S2", etc for SI pages)
        skip_si_toc: If True, skip first 2 pages of SI to avoid TOC
    """
    # Convert page number to int and handle S-prefix
    page_str = str(page_num).strip().upper()
    if page_str.startswith('S'):
        # Supplementary page - look in the SI PDF (second PDF)
        actual_page = int(page_str[1:]) - 1  # 0-indexed
        pdf_index = 1 if len(pdf_paths) > 1 else 0
        is_si_page = True
    else:
        # Regular page - look in the main PDF
        actual_page = int(page_str) - 1  # 0-indexed
        pdf_index = 0
        is_si_page = False
    
    # Skip first 2 pages of SI to avoid table of contents
    if skip_si_toc and is_si_page and actual_page < 2:
        log.info("Skipping SI page %s (first 2 pages are typically TOC)", page_str)
        return ""
    
    if pdf_index >= len(pdf_paths):
        log.warning("Page %s requested but not enough PDFs provided", page_str)
        return ""
    
    try:
        doc = fitz.open(pdf_paths[pdf_index])
        if 0 <= actual_page < len(doc):
            page = doc[actual_page]
            page_text = page.get_text()
            doc.close()
            log.info("Extracted %d chars from page %s of %s", 
                     len(page_text), page_str, pdf_paths[pdf_index].name)
            return page_text
        else:
            log.warning("Page %s (index %d) out of range for %s (has %d pages)", 
                       page_str, actual_page, pdf_paths[pdf_index].name, len(doc))
            doc.close()
            return ""
    except Exception as e:
        log.error("Failed to extract page %s: %s", page_str, e)
        return ""

# --- 7.3  Location validation with samples -----------------------------------
_LOC_VALIDATION_PROMPT = """
Which sample contains ACTUAL protein/DNA sequences (long strings of ACDEFGHIKLMNPQRSTVWY or ACGT)?
Not mutation lists, but actual sequences.

{samples}

Reply with ONLY a number: the location_id of the best sample (or -1 if none have sequences).
""".strip()

def validate_sequence_locations(text: str, locations: list, model, *, pdf_paths: List[Path] = None, debug_dir: str | Path | None = None) -> dict:
    """Extract samples from each location and ask Gemini to pick the best one."""
    if not locations:
        return {"best_location_id": -1, "reason": "No locations provided"}
    
    # Extract 500 char samples from each location
    samples = []
    for i, location in enumerate(locations[:5]):  # Limit to 5 locations
        sample_text = ""
        
        # If we have PDFs and location has a page number, use page extraction
        if pdf_paths and isinstance(location, dict) and 'page' in location:
            page_num = location['page']
            page_text = _extract_text_from_page(pdf_paths, page_num)
            
            # Also try to extract from the next page
            next_page_text = ""
            try:
                page_str = str(page_num).strip().upper()
                if page_str.startswith('S'):
                    next_page = f"S{int(page_str[1:]) + 1}"
                else:
                    next_page = str(int(page_str) + 1)
                next_page_text = _extract_text_from_page(pdf_paths, next_page)
            except:
                pass
            
            # Combine both pages
            combined_text = page_text + "\n" + next_page_text if next_page_text else page_text
            
            if combined_text:
                # Find the section within the combined pages if possible
                section = location.get('section', location.get('text', ''))
                if section:
                    # Try to find section in pages
                    section_lower = section.lower()
                    combined_lower = combined_text.lower()
                    pos = combined_lower.find(section_lower)
                    if pos >= 0:
                        # Extract from section start
                        sample_text = combined_text[pos:pos+5000]
                    else:
                        # Section not found, take from beginning
                        sample_text = combined_text[:10000]
                else:
                    # No section, take from beginning
                    sample_text = combined_text[:10000]
        
        # Fallback to text search if page extraction didn't work
        if not sample_text:
            sample_text = _extract_text_at_locations(
                text, [location], context_chars=20000, validate_sequences=False
            )
        
        samples.append({
            "location_id": i,
            "location": str(location),
            "sample": sample_text[:5000] if sample_text else ""
        })
    
    # Ask Gemini to analyze samples
    prompt = _LOC_VALIDATION_PROMPT.format(samples=json.dumps(samples, indent=2))
    
    # Save prompt for debugging
    if debug_dir:
        _dump(f"=== PROMPT FOR LOCATION_VALIDATION ===\nTimestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\nLength: {len(prompt)} characters\n{'='*80}\n\n{prompt}",
              Path(debug_dir) / f"location_validation_prompt_{int(time.time())}.txt")
    
    try:
        # Get simple numeric response from Gemini
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Save response for debugging
        if debug_dir:
            _dump(f"=== RESPONSE FOR LOCATION_VALIDATION ===\nTimestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\nLength: {len(response_text)} characters\n{'='*80}\n\n{response_text}",
                  Path(debug_dir) / f"location_validation_response_{int(time.time())}.txt")
        
        # Try to extract the number from response
        match = re.search(r'-?\d+', response_text)
        if match:
            best_id = int(match.group())
            return {"best_location_id": best_id, "reason": "Selected by Gemini"}
        else:
            log.warning("Could not parse location ID from response: %s", response_text)
            return {"best_location_id": -1, "reason": "Could not parse response"}
            
    except Exception as exc:
        log.warning("validate_sequence_locations(): %s", exc)
        return {"best_location_id": -1, "reason": str(exc)}

# --- 7.3  Main extraction prompt ---------------------------------------------
_SEQ_EXTRACTION_PROMPT = """
Extract ALL enzyme variant sequences from the text. Copy sequences EXACTLY as they appear - character by character.

KEY RULES:
1. EXHAUSTIVE SEARCH: If a variant appears multiple times, check ALL occurrences and extract the LONGEST sequence
2. MULTI-PAGE: Sequences span pages. Be careful to extract the WHOLE sequence - sequences are often split across pages and you must capture the complete sequence, not just the part on one page
3. MERGE IF NEEDED: If sequence continues after page break, combine the parts
4. NO MODIFICATIONS: Copy exactly - no edits or improvements
5. ONLY VISIBLE SEQUENCES: You are a COPIER, not a creator. Extract ONLY sequences you can actually SEE in the document
   - DO NOT add sequences you think should be there
   - DO NOT fill in missing sequences based on patterns
   - If a variant is mentioned but has no visible sequence, DO NOT include it

IMPORTANT: The same variant may appear multiple times with different sequence lengths. Always use the longest one.

⚠️ CHARACTER RECOGNITION WARNING: ⚠️
When reading variant IDs and sequences:
- Do NOT confuse "O" (letter) with "0" (zero)
- Do NOT confuse "l" (lowercase L) with "1" (one)
- Do NOT confuse "I" (uppercase i) with "1" (one)
- In variant names like "L-G0", the last character is a zero (0), not letter O
- In mutations like "L34V", the L is a letter (leucine), not number 1

SEQUENCE PRIORITY:
- If BOTH amino acid AND DNA exist → use amino acid ONLY
- For DNA: If mixed case, extract UPPERCASE only (lowercase=backbone)
- Return minified JSON only

ACCURACY:
- Extract ONLY what's written and VISIBLE in the document
- Never hallucinate or add sequences that aren't shown
- Check entire document - complete sequences often appear later
- You are a SEQUENCE COPIER: If you can't see the actual sequence, don't include that variant
- Empty results are better than made-up sequences

IMPORTANT: If NO sequences are found in the text:
- Return an empty array: []
- Do NOT make up or hallucinate sequences
- An empty response is valid when no sequences exist

Schema: {schema}

TEXT:
{text}
""".strip()

def _check_sequence_responses_match(resp1: Union[list, dict], resp2: Union[list, dict]) -> bool:
    """
    Check if two sequence extraction responses match.
    
    Args:
        resp1: First response (list of sequences or dict)
        resp2: Second response (list of sequences or dict)
        
    Returns:
        True if responses match, False otherwise
    """
    # Handle None cases
    if resp1 is None or resp2 is None:
        return False
    
    # Both should be the same type
    if type(resp1) != type(resp2):
        return False
    
    # If both are lists
    if isinstance(resp1, list) and isinstance(resp2, list):
        # Must have same length
        if len(resp1) != len(resp2):
            return False
        
        # Create normalized sequence sets for comparison
        seq_set1 = set()
        seq_set2 = set()
        
        for seq in resp1:
            if isinstance(seq, dict):
                variant_id = seq.get("variant_id", "")
                aa_seq = seq.get("aa_seq")
                dna_seq = seq.get("dna_seq")
                # Handle None/null values - convert to empty string for comparison
                if aa_seq is None:
                    aa_seq = ""
                else:
                    aa_seq = aa_seq.replace(" ", "").replace("\n", "").upper()
                if dna_seq is None:
                    dna_seq = ""
                else:
                    dna_seq = dna_seq.replace(" ", "").replace("\n", "").upper()
                seq_set1.add(f"{variant_id}|{aa_seq}|{dna_seq}")
        
        for seq in resp2:
            if isinstance(seq, dict):
                variant_id = seq.get("variant_id", "")
                aa_seq = seq.get("aa_seq")
                dna_seq = seq.get("dna_seq")
                # Handle None/null values - convert to empty string for comparison
                if aa_seq is None:
                    aa_seq = ""
                else:
                    aa_seq = aa_seq.replace(" ", "").replace("\n", "").upper()
                if dna_seq is None:
                    dna_seq = ""
                else:
                    dna_seq = dna_seq.replace(" ", "").replace("\n", "").upper()
                seq_set2.add(f"{variant_id}|{aa_seq}|{dna_seq}")
        
        return seq_set1 == seq_set2
    
    # If both are dicts, compare normalized content
    if isinstance(resp1, dict) and isinstance(resp2, dict):
        # Normalize and compare
        return json.dumps(resp1, sort_keys=True) == json.dumps(resp2, sort_keys=True)
    
    return False


def _extract_sequences_with_triple_validation(model, prompt_or_content, schema_hint: str, *, debug_dir: str | Path | None = None) -> Optional[Any]:
    """Extract sequence JSON using Gemini with up to 3 attempts, returning most common result.
    
    Can exit early after 2 attempts if the responses match exactly.
    
    Args:
        model: The Gemini model instance
        prompt_or_content: Either a string prompt or list of multimodal content parts
        schema_hint: The JSON schema hint
        debug_dir: Optional debug directory
    
    Returns:
        The most common sequence JSON data or None if all attempts failed
    """
    responses = []
    max_attempts = 5  # 5 attempts for better consensus
    
    # Try 5 times with early match detection
    for attempt in range(max_attempts):
        try:
            log.info(f"Sequence extraction attempt {attempt + 1}/{max_attempts}")
            resp = model.generate_content(prompt_or_content)
            
            # Debug the response object
            log.debug(f"Response type: {type(resp)}")
            log.debug(f"Has candidates: {hasattr(resp, 'candidates')}")
            if hasattr(resp, 'candidates'):
                log.debug(f"Number of candidates: {len(resp.candidates) if resp.candidates else 0}")
                if resp.candidates and len(resp.candidates) > 0:
                    log.debug(f"Candidate 0 finish reason: {getattr(resp.candidates[0], 'finish_reason', 'N/A')}")
            
            raw = _extract_text(resp).strip()
            log.debug(f"Extracted text length: {len(raw)}")
            
            # If extraction failed, try to access the text directly as a fallback
            if not raw and hasattr(resp, 'text'):
                log.warning("Text extraction returned empty, trying direct access")
                raw = resp.text.strip()
            elif not raw and hasattr(resp, 'candidates') and resp.candidates:
                log.warning("Text extraction returned empty, trying manual extraction")
                if hasattr(resp.candidates[0], 'content') and hasattr(resp.candidates[0].content, 'parts'):
                    text_parts = []
                    for part in resp.candidates[0].content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
                    if text_parts:
                        raw = "".join(text_parts).strip()
                        log.info(f"Manual extraction recovered {len(raw)} characters")
            
            # Save debug info BEFORE text extraction to capture the actual response
            if debug_dir:
                debug_path = Path(debug_dir)
                debug_path.mkdir(parents=True, exist_ok=True)
                response_file = debug_path / f"sequences_attempt_{attempt + 1}_{int(time.time())}.txt"
                with open(response_file, 'w') as f:
                    f.write(f"=== SEQUENCE EXTRACTION ATTEMPT {attempt + 1} ===\n")
                    f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Response object type: {type(resp)}\n")
                    if hasattr(resp, 'candidates'):
                        f.write(f"Candidates: {len(resp.candidates) if resp.candidates else 0} candidates\n")
                        if resp.candidates and len(resp.candidates) > 0:
                            f.write(f"Finish reason: {getattr(resp.candidates[0], 'finish_reason', 'N/A')}\n")
                            f.write(f"Safety ratings: {getattr(resp.candidates[0], 'safety_ratings', 'N/A')}\n")
                            # Try to extract text manually for debugging
                            if hasattr(resp.candidates[0], 'text'):
                                f.write(f"Direct text access: {len(resp.candidates[0].text)} chars\n")
                            if hasattr(resp.candidates[0], 'content'):
                                f.write(f"Has content attribute\n")
                                if hasattr(resp.candidates[0].content, 'parts'):
                                    f.write(f"Number of parts: {len(resp.candidates[0].content.parts)}\n")
                                    for i, part in enumerate(resp.candidates[0].content.parts):
                                        if hasattr(part, 'text'):
                                            f.write(f"Part {i} text length: {len(part.text) if part.text else 0}\n")
                    # Now extract and write the text
                    f.write(f"Extracted text length: {len(raw)} characters\n")
                    f.write("="*80 + "\n\n")
                    f.write(raw)
            
            # Parse JSON response (similar to generate_json_with_retry logic)
            # Save original for error reporting
            original_raw = raw
            
            # Check if response contains header information before JSON
            # This can happen with certain Gemini API responses
            if raw and not raw.lstrip().startswith(('[', '{')):
                # Look for where JSON actually starts
                lines = raw.split('\n')
                json_start_line = None
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith('[') or stripped.startswith('{') or stripped.lower().startswith('```json'):
                        json_start_line = i
                        break
                
                if json_start_line is not None:
                    # Extract only the JSON part
                    raw = '\n'.join(lines[json_start_line:])
                    log.debug(f"Removed {json_start_line} header lines, new length: {len(raw)}")
            
            # Remove code fences if present
            if "```json" in raw.lower() or "```" in raw:
                fence_re = re.compile(r"```json\s*|```", re.I)
                raw = fence_re.sub("", raw).strip()
                log.debug(f"Removed code fences, new length: {len(raw)}")
            
            # Try to parse as JSON
            try:
                # First clean the response - remove any BOM or invisible characters
                log.debug(f"raw before cleaning: length={len(raw)}, type={type(raw)}")
                raw_clean = raw.strip()
                log.debug(f"raw_clean after strip: length={len(raw_clean)}")
                if raw_clean.startswith('\ufeff'):  # Remove BOM if present
                    raw_clean = raw_clean[1:]
                    log.debug("Removed BOM character")
                
                # Check if raw_clean is empty before parsing
                if not raw_clean:
                    log.error("raw_clean is empty after stripping!")
                    log.error(f"Original raw length: {len(raw)}")
                    log.error(f"Original raw type: {type(raw)}")
                    log.error(f"Original raw repr: {repr(raw[:200]) if raw else 'None or empty'}")
                    log.error(f"raw == '': {raw == ''}")
                    log.error(f"raw is None: {raw is None}")
                    # Check what the response object contains
                    if hasattr(resp, 'candidates') and resp.candidates:
                        log.error("Response has candidates, trying direct extraction...")
                        if hasattr(resp.candidates[0], 'text'):
                            log.error(f"Candidate text: {repr(resp.candidates[0].text[:200])}")
                    raise ValueError("Empty response after cleaning")
                
                # Try direct parsing first
                log.debug(f"About to parse JSON, raw_clean length: {len(raw_clean)}")
                log.debug(f"raw_clean first 200 chars: {repr(raw_clean[:200])}")
                
                # Make sure we have something to parse
                if not raw_clean or not raw_clean.strip():
                    raise ValueError(f"Empty JSON string to parse. raw={len(raw)}, raw_clean={len(raw_clean)}")
                
                # Try to parse - if it fails, try to clean up common issues
                try:
                    parsed = json.loads(raw_clean)
                except json.JSONDecodeError as parse_error:
                    # Try removing any zero-width spaces or other invisible characters
                    import unicodedata
                    cleaned = ''.join(ch for ch in raw_clean if unicodedata.category(ch)[0] != 'C' or ch in '\n\r\t')
                    log.warning(f"Initial parse failed, trying with cleaned string. Original len: {len(raw_clean)}, cleaned len: {len(cleaned)}")
                    parsed = json.loads(cleaned)
            except json.JSONDecodeError as e:
                log.error(f"Initial JSON parsing failed: {e}")
                log.error(f"Error position: {e.pos}")
                log.error(f"raw length: {len(raw)}")
                log.error(f"raw_clean length: {len(raw_clean)}")
                log.error(f"raw == raw_clean: {raw == raw_clean}")
                log.error(f"Response starts with: {repr(raw[:100])}")
                log.error(f"Response ends with: {repr(raw[-100:] if len(raw) > 100 else raw)}")
                # Look for JSON array or object in the response
                json_start = -1
                json_end = -1
                bracket_stack = []
                in_string = False
                escape_next = False
                
                for i, char in enumerate(raw):
                    if escape_next:
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        continue
                        
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        continue
                    
                    if in_string:
                        continue
                    
                    if char in '[{':
                        if json_start == -1:
                            json_start = i
                        bracket_stack.append(char)
                    elif char in ']}':
                        if bracket_stack:
                            opening = bracket_stack.pop()
                            if (opening == '[' and char == ']') or (opening == '{' and char == '}'):
                                if not bracket_stack:  # Found complete JSON
                                    json_end = i + 1
                                    break
                
                if json_start >= 0 and json_end > json_start:
                    json_str = raw[json_start:json_end]
                    parsed = json.loads(json_str)
                else:
                    if '[]' in raw:
                        parsed = []
                    else:
                        # Provide more context in error message using original response
                        preview = original_raw[:200] + "..." if len(original_raw) > 200 else original_raw
                        error_msg = f"No JSON structure found in response. Response preview: {repr(preview)}"
                        log.error(error_msg)
                        log.error(f"Raw after processing: {repr(raw[:200]) if raw else 'EMPTY'}")
                        raise json.JSONDecodeError(error_msg, original_raw, 0)
            
            # Store the response
            responses.append(parsed)
            log.info(f"Sequence extraction attempt {attempt + 1}: {len(parsed) if isinstance(parsed, list) else 'object'} sequences")
            
            # If we got a good response with sequences, we can check for early termination
            if isinstance(parsed, list) and len(parsed) > 0:
                # Early match detection after 2 attempts
                if attempt >= 1:  # After 2nd attempt (0-indexed)
                    valid_responses_so_far = [r for r in responses if r is not None and isinstance(r, list) and len(r) > 0]
                    if len(valid_responses_so_far) >= 2:
                        # Check if the last two valid responses match
                        if _check_sequence_responses_match(valid_responses_so_far[-2], valid_responses_so_far[-1]):
                            log.info(f"Early match detected after {attempt + 1} attempts - sequences are consistent")
                            # Add the matching response to fill remaining attempts
                            for _ in range(max_attempts - attempt - 1):
                                responses.append(valid_responses_so_far[-1])
                            break
                # If this is the first attempt and we got sequences, continue to validate with at least one more
                elif attempt == 0 and len(parsed) > 5:  # Got substantial sequences on first try
                    log.info("Got substantial sequences on first attempt, will validate with one more")
            
        except Exception as e:
            log.warning(f"Sequence extraction attempt {attempt + 1} failed: {e}")
            responses.append(None)
    
    # After all attempts, find most common sequences
    valid_responses = [r for r in responses if r is not None]
    
    if not valid_responses:
        log.error(f"All {max_attempts} sequence extraction attempts failed")
        return None
    
    # Count occurrences of each individual sequence across all attempts
    sequence_counts = {}
    for resp in valid_responses:
        if isinstance(resp, list):
            for seq in resp:
                if isinstance(seq, dict) and "variant_id" in seq:
                    # Create a key for this sequence (variant_id + cleaned sequence)
                    variant_id = seq.get("variant_id", "")
                    aa_seq = seq.get("aa_seq", "")
                    dna_seq = seq.get("dna_seq", "")
                    
                    # Clean sequences for comparison
                    if aa_seq:
                        aa_seq = aa_seq.replace(" ", "").replace("\n", "").upper()
                    if dna_seq:
                        dna_seq = dna_seq.replace(" ", "").replace("\n", "").upper()
                    
                    # Use whichever sequence is present for the key
                    seq_for_key = aa_seq if aa_seq else (dna_seq if dna_seq else "")
                    key = f"{variant_id}|{seq_for_key}"
                    
                    if key not in sequence_counts:
                        sequence_counts[key] = {"count": 0, "data": seq}
                    sequence_counts[key]["count"] += 1
    
    # Build result with sequences that appear in at least 2 attempts
    # Sort by count (descending) to prioritize sequences with higher consensus
    result = []
    sorted_sequences = sorted(sequence_counts.items(), key=lambda x: x[1]["count"], reverse=True)
    
    for key, info in sorted_sequences:
        if info["count"] >= 2:  # Appears in at least 2/5 attempts
            seq_data = info["data"].copy()
            seq_data["extraction_confidence"] = f"{info['count']}/{max_attempts}"
            result.append(seq_data)
            log.info(f"Sequence {seq_data.get('variant_id')} appeared in {info['count']}/{max_attempts} attempts")
    
    if result:
        log.info(f"Extracted {len(result)} sequences with at least 2/{max_attempts} consensus")
        return result
    
    # If no sequences appear twice, return the most complete attempt
    best_attempt = max(valid_responses, key=lambda x: len(x) if isinstance(x, list) else 0)
    log.warning(f"No consensus sequences found, returning best attempt with {len(best_attempt)} sequences")
    return best_attempt




def extract_sequences(text: str, model, *, debug_dir: str | Path | None = None, lineage_context: str = None, lineage_variants: List[Variant] = None) -> list[SequenceBlock]:
    """Prompt Gemini and convert its JSON reply into SequenceBlock objects with triple validation."""
    base_prompt = _SEQ_EXTRACTION_PROMPT.format(
        schema=_SEQUENCE_SCHEMA_HINT, text=text[:MAX_CHARS]
    )
    
    # Add lineage context if available
    if lineage_context:
        prompt = f"""{base_prompt}

IMPORTANT CONTEXT - Known variants from lineage extraction:
{lineage_context}

Match sequences to these known variants when possible. Variants may be labeled differently in different sections (e.g., "5295" might also appear as "ʟ-G0", "ʟ-ApPgb-αEsA-G0", or "ʟ-ApPgb-αEsA-G0 (5295)").
"""
    else:
        prompt = base_prompt
    
    # Skip mutation validation context
    
    # Save the complete prompt for debugging
    if debug_dir:
        debug_path = Path(debug_dir)
        debug_path.mkdir(parents=True, exist_ok=True)
        prompt_file = debug_path / f"sequence_extraction_prompt_{int(time.time())}.txt"
        with open(prompt_file, 'w') as f:
            f.write(f"=== SEQUENCE EXTRACTION PROMPT ===\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Text length: {len(text)} characters\n")
            f.write(f"Truncated to: {len(text[:MAX_CHARS])} characters\n")
            f.write(f"Total prompt length: {len(prompt)} characters\n")
            f.write("="*80 + "\n\n")
            f.write(prompt)
        log.info(f"Saved sequence extraction prompt to {prompt_file}")
    
    # Use triple validation for sequence extraction
    log.info("Extracting sequences with triple validation to ensure accuracy")
    data = _extract_sequences_with_triple_validation(model, prompt, _SEQUENCE_SCHEMA_HINT, debug_dir=debug_dir)
    
    if not data:
        log.warning("Failed to get consistent sequence extraction after triple validation")
        return []
    
    extracted_sequences = _parse_sequences(data)
    
    # Return extracted sequences without mutation validation
    return extracted_sequences

# --- 7.4  JSON -> dataclass helpers -------------------------------------------
_VALID_AA  = set("ACDEFGHIKLMNPQRSTVWY*")  # Include * for stop codon
_VALID_DNA = set("ACGT")

def _contains_sequence(text: str, min_length: int = 50) -> bool:
    """Check if text contains likely protein or DNA sequences."""
    # Remove whitespace for checking
    clean_text = re.sub(r'\s+', '', text.upper())
    
    # Check for continuous stretches of valid amino acids or DNA
    # Look for at least min_length consecutive valid characters
    aa_pattern = f"[{''.join(_VALID_AA)}]{{{min_length},}}"
    dna_pattern = f"[{''.join(_VALID_DNA)}]{{{min_length},}}"
    
    return bool(re.search(aa_pattern, clean_text) or re.search(dna_pattern, clean_text))

def _clean_seq(seq: str | None, alphabet: set[str]) -> str | None:
    if not seq:
        return None
    seq = re.sub(r"\s+", "", seq).upper()
    return seq if seq and all(ch in alphabet for ch in seq) else None

def _parse_sequences(raw: list[dict]) -> list[SequenceBlock]:
    """Validate and convert raw JSON into SequenceBlock instances."""
    blocks: list[SequenceBlock] = []
    for entry in raw:
        vid = (entry.get("variant_id") or entry.get("id") or "").strip()
        if not vid:
            continue
        aa  = _clean_seq(entry.get("aa_seq"),  _VALID_AA)
        dna = _clean_seq(entry.get("dna_seq"), _VALID_DNA)

        # Check minimum length requirements
        # AA sequences should be > 50, DNA sequences should be > 150
        if aa and len(aa) <= 50:
            log.debug(f"Skipping short AA sequence for {vid}: {len(aa)} amino acids")
            aa = None
        
        # Validate DNA sequences
        if dna:
            if len(dna) <= 150:
                log.debug(f"Skipping short DNA sequence for {vid}: {len(dna)} nucleotides")
                dna = None
            # Check if DNA sequence length is divisible by 3
            # elif len(dna) % 3 != 0:
            #     log.debug(f"Skipping DNA sequence for {vid}: length {len(dna)} not divisible by 3")
            #     dna = None
            else:
                # Check for stop codons in the middle of the sequence
                stop_codons = {'TAA', 'TAG', 'TGA'}
                has_internal_stop = False
                for i in range(0, len(dna) - 3, 3):
                    codon = dna[i:i+3]
                    if codon in stop_codons:
                        log.warning(f"Skipping DNA sequence for {vid}: internal stop codon {codon} at position {i}")
                        has_internal_stop = True
                        break
                if has_internal_stop:
                    dna = None

        # Skip if both sequences are invalid or missing
        if not aa and not dna:
            continue

        conf: float | None = None
        if aa:
            conf = sum(c in _VALID_AA  for c in aa)  / len(aa)
        elif dna:
            conf = sum(c in _VALID_DNA for c in dna) / len(dna)

        blocks.append(
            SequenceBlock(
                variant_id=vid,
                aa_seq=aa,
                dna_seq=dna,
                confidence=conf,
                truncated=False,
            )
        )
    return blocks

def _build_mutation_validation_context(lineage_variants: List[Variant]) -> str:
    """Build mutation context for sequence validation."""
    mutation_info = []
    
    for variant in lineage_variants:
        if variant.mutations and variant.parent_id:
            mutations_str = "; ".join(variant.mutations) if isinstance(variant.mutations, list) else str(variant.mutations)
            mutation_info.append(f"Variant '{variant.variant_id}' (parent: '{variant.parent_id}') has mutations: {mutations_str}")
    
    if not mutation_info:
        return ""
    
    context = "Known mutation relationships:\n" + "\n".join(mutation_info[:10])  # Limit to first 10 for context
    if len(mutation_info) > 10:
        context += f"\n... and {len(mutation_info) - 10} more variants with mutations"
    
    return context

def _validate_sequences_against_mutations(sequences: List[SequenceBlock], lineage_variants: List[Variant], model, debug_dir: str | Path | None = None) -> List[SequenceBlock]:
    """Validate extracted sequences against known mutations and fix inconsistencies."""
    # Create lookups for easier access
    seq_lookup = {seq.variant_id: seq for seq in sequences}
    variant_lookup = {var.variant_id: var for var in lineage_variants}
    
    validation_issues = []
    corrected_sequences = []
    
    for seq in sequences:
        variant = variant_lookup.get(seq.variant_id)
        if not variant or not variant.parent_id or not variant.mutations or not seq.aa_seq:
            corrected_sequences.append(seq)
            continue
        
        parent_seq = seq_lookup.get(variant.parent_id)
        if not parent_seq or not parent_seq.aa_seq:
            corrected_sequences.append(seq)
            continue
        
        # Check if mutations are consistent
        issues = _check_mutation_consistency(seq.aa_seq, parent_seq.aa_seq, variant.mutations, seq.variant_id, variant.parent_id)
        
        if issues:
            validation_issues.extend(issues)
            log.warning(f"Sequence validation issues for {seq.variant_id}: {'; '.join(issues)}")
            
            # Try to get corrected sequence from Gemini
            corrected_seq = _get_corrected_sequence_from_gemini(seq, parent_seq, variant, issues, model, debug_dir)
            if corrected_seq:
                corrected_sequences.append(corrected_seq)
                log.info(f"Corrected sequence for {seq.variant_id} using Gemini validation")
            else:
                # STRICT RULE: If mutations don't match and correction fails, leave sequence empty
                empty_seq = SequenceBlock(
                    variant_id=seq.variant_id,
                    aa_seq="",  # Empty sequence due to validation failure
                    dna_seq="",  # Empty DNA sequence as well
                    confidence=0.0,
                    truncated=False
                )
                corrected_sequences.append(empty_seq)
                log.warning(f"Cleared sequence for {seq.variant_id} due to mutation validation failure")
        else:
            corrected_sequences.append(seq)
    
    if validation_issues:
        log.warning(f"Found {len(validation_issues)} sequence validation issues across {len([s for s in sequences if s.variant_id in [v.variant_id for v in lineage_variants if v.mutations]])} variants with mutations")
    
    return corrected_sequences

def _check_mutation_consistency(child_seq: str, parent_seq: str, mutations, child_id: str, parent_id: str) -> List[str]:
    """Check if mutations are consistent between parent and child sequences."""
    import re
    
    issues = []
    
    # Parse mutations (handle both string and list formats)
    if isinstance(mutations, list):
        mutation_strs = mutations
    else:
        mutation_strs = [m.strip() for m in str(mutations).split(',') if m.strip()]
    
    for mut_str in mutation_strs:
        # Parse mutation like "A100V"
        match = re.match(r'^([A-Z])(\d+)([A-Z])$', mut_str.strip())
        if not match:
            continue  # Skip non-standard mutation formats
        
        orig_aa, pos_str, new_aa = match.groups()
        pos = int(pos_str) - 1  # Convert to 0-based indexing
        
        # Check bounds
        if pos >= len(parent_seq) or pos >= len(child_seq):
            issues.append(f"Mutation {mut_str} position out of bounds")
            continue
        
        # Check parent sequence has expected original amino acid
        if parent_seq[pos] != orig_aa:
            issues.append(f"Mutation {mut_str}: parent {parent_id} has {parent_seq[pos]} at position {pos+1}, expected {orig_aa}")
        
        # Check child sequence has expected new amino acid
        if child_seq[pos] != new_aa:
            issues.append(f"Mutation {mut_str}: child {child_id} has {child_seq[pos]} at position {pos+1}, expected {new_aa}")
    
    return issues

def _get_corrected_sequence_from_gemini(seq: SequenceBlock, parent_seq: SequenceBlock, variant: Variant, issues: List[str], model, debug_dir: str | Path | None = None) -> SequenceBlock | None:
    """Use Gemini to get a corrected sequence based on mutation validation issues."""
    if not model:
        return None
    
    mutations_str = "; ".join(variant.mutations) if isinstance(variant.mutations, list) else str(variant.mutations)
    issues_str = "; ".join(issues)
    
    prompt = f"""You extracted a sequence for variant "{seq.variant_id}" but there are mutation validation issues:

ISSUES: {issues_str}

PARENT SEQUENCE ({variant.parent_id}):
{parent_seq.aa_seq}

EXTRACTED SEQUENCE ({seq.variant_id}):
{seq.aa_seq}

EXPECTED MUTATIONS: {mutations_str}

Based on the parent sequence and the expected mutations, provide the CORRECT sequence for {seq.variant_id}.
Apply each mutation to the parent sequence in order.

For example, if parent has "A" at position 100 and mutation is "A100V", then child should have "V" at position 100.

IMPORTANT SEQUENCE RULES:
- Copy the sequence EXACTLY - do not add, remove, or modify any amino acids
- Pay careful attention to repeated amino acids (e.g., "AAA" should remain "AAA", not become "A")
- Preserve the exact length of the sequence
- Only change the specific positions indicated by the mutations
- Double-check that consecutive identical amino acids are copied correctly

Return ONLY the corrected amino acid sequence (no explanation, no formatting).
If you cannot determine the correct sequence, return "UNCERTAIN".
"""
    
    try:
        if debug_dir:
            import time
            timestamp = int(time.time())
            prompt_file = Path(debug_dir) / f"sequence_validation_{seq.variant_id}_{timestamp}.txt"
            _dump(prompt, prompt_file)
        
        # Use triple validation for sequence correction
        log.info(f"Correcting sequence for {seq.variant_id} with triple validation")
        corrected_seq = _extract_plain_sequence_with_triple_validation(prompt, model, f"correction for {seq.variant_id}")
        
        if debug_dir and corrected_seq:
            response_file = Path(debug_dir) / f"sequence_validation_response_{seq.variant_id}_{timestamp}.txt"
            _dump(corrected_seq, response_file)
        
        if corrected_seq and corrected_seq not in ["UNCERTAIN", "VALID"] and _clean_seq(corrected_seq, _VALID_AA):
            return SequenceBlock(
                variant_id=seq.variant_id,
                aa_seq=corrected_seq,
                dna_seq=seq.dna_seq,
                confidence=0.8,  # Lower confidence for corrected sequences
                truncated=seq.truncated
            )
    
    except Exception as e:
        log.warning(f"Failed to get corrected sequence for {seq.variant_id}: {e}")
    
    return None

# --- 7.5  Convenience wrapper -------------------------------------------------
def get_sequences(text: str, model, *, pdf_paths: List[Path] = None, debug_dir: str | Path | None = None, lineage_variants: List[Variant] = None) -> list[SequenceBlock]:
    """Extract sequences using full PDFs instead of location-based extraction."""
    log.info("Using full PDF extraction for sequences")
    
    # Build lineage context if available
    lineage_context = None
    if lineage_variants:
        variant_info = []
        for v in lineage_variants[:20]:  # Limit to first 20
            info = f"- {v.variant_id} (Gen {v.generation})"
            if v.mutations:
                info += f" [{', '.join(v.mutations[:3])}{'...' if len(v.mutations) > 3 else ''}]"
            variant_info.append(info)
        lineage_context = "\n".join(variant_info)
    
    # If we have PDFs, use multimodal extraction
    if pdf_paths:
        log.info("Extracting sequences using multimodal API with PDFs")
        return extract_sequences_multimodal(pdf_paths, model, debug_dir=debug_dir, lineage_context=lineage_context, lineage_variants=lineage_variants)
    else:
        # Fallback to text-based extraction
        log.info("No PDFs available, using text-based sequence extraction")
        return extract_sequences(text, model, debug_dir=debug_dir, lineage_context=lineage_context, lineage_variants=lineage_variants)

def extract_sequences_multimodal(pdf_paths: List[Path], model, *, debug_dir: str | Path | None = None, lineage_context: str = None, lineage_variants: List[Variant] = None) -> list[SequenceBlock]:
    """Extract sequences using multimodal API with PDFs."""
    
    # Build the base prompt for multimodal (without text section)
    base_prompt = """Extract ALL enzyme variant sequences from the attached PDF documents. Copy sequences EXACTLY as they appear - character by character.

KEY RULES:
1. EXHAUSTIVE SEARCH: If a variant appears multiple times, check ALL occurrences and extract the LONGEST sequence
2. MULTI-PAGE: Sequences span pages. Be careful to extract the WHOLE sequence - sequences are often split across pages and you must capture the complete sequence, not just the part on one page
3. MERGE IF NEEDED: If sequence continues after page break, combine the parts
4. NO MODIFICATIONS: Copy exactly - no edits or improvements
5. ONLY VISIBLE SEQUENCES: You are a COPIER, not a creator. Extract ONLY sequences you can actually SEE in the document
   - DO NOT add sequences you think should be there
   - DO NOT fill in missing sequences based on patterns
   - If a variant is mentioned but has no visible sequence, DO NOT include it

IMPORTANT: The same variant may appear multiple times with different sequence lengths. Always use the longest one.

⚠️ CHARACTER RECOGNITION WARNING: ⚠️
When reading variant IDs and sequences:
- Do NOT confuse "O" (letter) with "0" (zero)
- Do NOT confuse "l" (lowercase L) with "1" (one)
- Do NOT confuse "I" (uppercase i) with "1" (one)
- In variant names like "L-G0", the last character is a zero (0), not letter O
- In mutations like "L34V", the L is a letter (leucine), not number 1

SEQUENCE PRIORITY:
- If BOTH amino acid AND DNA exist → use amino acid ONLY
- For DNA: If mixed case, extract UPPERCASE only (lowercase=backbone)
- Return minified JSON only

ACCURACY:
- Extract ONLY what's written and VISIBLE in the document
- Never hallucinate or add sequences that aren't shown
- Check entire document - complete sequences often appear later
- You are a SEQUENCE COPIER: If you can't see the actual sequence, don't include that variant
- Empty results are better than made-up sequences

IMPORTANT: If NO sequences are found in the PDFs:
- Return an empty array: []
- Do NOT make up or hallucinate sequences
- An empty response is valid when no sequences exist

Schema: {schema}""".format(schema=_SEQUENCE_SCHEMA_HINT)
    
    # Add lineage context if available
    if lineage_context:
        prompt = f"""{base_prompt}

IMPORTANT CONTEXT - Known variants from lineage extraction:
{lineage_context}

Match sequences to these known variants when possible. Variants may be labeled differently in different sections.
"""
    else:
        prompt = base_prompt
    
    # Prepare multimodal content with PDFs
    content_parts = [prompt]
    
    # Add PDFs to the multimodal request
    for pdf_path in pdf_paths:
        if pdf_path and pdf_path.exists():
            doc_type = "Manuscript" if "si" not in str(pdf_path).lower() else "Supporting Information"
            log.info(f"Adding {doc_type} PDF to multimodal request for sequence extraction")
            
            try:
                pdf_bytes = pdf_path.read_bytes()
                # Create a blob dict for the PDF content
                pdf_blob = {
                    "mime_type": "application/pdf",
                    "data": pdf_bytes
                }
                content_parts.append(f"\n\n[{doc_type} PDF]")
                content_parts.append(pdf_blob)
            except Exception as e:
                log.warning(f"Failed to read PDF {pdf_path}: {e}")
    
    # Save debug info if requested
    if debug_dir:
        debug_path = Path(debug_dir)
        debug_path.mkdir(parents=True, exist_ok=True)
        prompt_file = debug_path / f"sequence_extraction_multimodal_prompt_{int(time.time())}.txt"
        with open(prompt_file, 'w') as f:
            f.write(f"=== MULTIMODAL SEQUENCE EXTRACTION PROMPT ===\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"PDFs: {[p.name for p in pdf_paths]}\n")
            f.write(f"{'='*80}\n\n")
            f.write(prompt)
        log.info(f"Saved multimodal sequence extraction prompt to {prompt_file}")
    
    # Extract sequences using multimodal API
    try:
        result = _extract_sequences_with_triple_validation(
            model, 
            content_parts,  # Pass the multimodal content
            _SEQUENCE_SCHEMA_HINT,
            debug_dir=debug_dir
        )
        
        if result:
            # Convert to SequenceBlock objects
            sequences = []
            for item in result:
                try:
                    seq_block = SequenceBlock(
                        variant_id=item["variant_id"],
                        aa_seq=item.get("aa_seq"),
                        dna_seq=item.get("dna_seq")
                    )
                    sequences.append(seq_block)
                except Exception as e:
                    log.warning(f"Failed to create SequenceBlock: {e}")
            
            log.info(f"Extracted {len(sequences)} sequences using multimodal API")
            return sequences
        else:
            log.warning("Multimodal sequence extraction returned no results")
            return []
            
    except Exception as e:
        log.error(f"Multimodal sequence extraction failed: {e}")
        return []

# === 7.6 PDB SEQUENCE EXTRACTION === -----------------------------------------
"""When no sequences are found in the paper, attempt to fetch them from PDB."""

def fetch_pdb_sequences(pdb_id: str) -> Dict[str, str]:
    """Fetch protein sequences from PDB using RCSB API.
    
    Returns dict mapping chain IDs to sequences.
    """
    # Use the GraphQL API which is more reliable
    url = "https://data.rcsb.org/graphql"
    
    query = """
    query getSequences($pdb_id: String!) {
        entry(entry_id: $pdb_id) {
            polymer_entities {
                entity_poly {
                    pdbx_seq_one_letter_code_can
                }
                rcsb_polymer_entity_container_identifiers {
                    auth_asym_ids
                }
            }
        }
    }
    """
    
    try:
        import requests
        response = requests.post(
            url, 
            json={"query": query, "variables": {"pdb_id": pdb_id.upper()}},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        sequences = {}
        entry_data = data.get('data', {}).get('entry', {})
        
        if entry_data:
            for entity in entry_data.get('polymer_entities', []):
                # Get sequence
                seq_data = entity.get('entity_poly', {})
                sequence = seq_data.get('pdbx_seq_one_letter_code_can', '')
                
                # Get chain IDs
                chain_data = entity.get('rcsb_polymer_entity_container_identifiers', {})
                chain_ids = chain_data.get('auth_asym_ids', [])
                
                if sequence and chain_ids:
                    # Clean sequence - remove newlines and spaces
                    clean_seq = sequence.replace('\n', '').replace(' ', '').upper()
                    
                    # Add sequence for each chain
                    for chain_id in chain_ids:
                        sequences[chain_id] = clean_seq
                        log.info(f"PDB {pdb_id} chain {chain_id}: {len(clean_seq)} residues")
        
        return sequences
        
    except Exception as e:
        log.warning(f"Failed to fetch PDB {pdb_id}: {e}")
        return {}


def extract_enzyme_info_with_gemini(
    text: str,
    variants: List[Variant],
    model,
) -> Dict[str, str]:
    """Use Gemini to extract enzyme names or sequences when PDB IDs are not available.
    
    Returns:
        Dict mapping variant IDs to sequences
    """
    # Build variant info for context
    variant_info = []
    for v in variants[:10]:  # Limit to first 10 variants for context
        info = {
            "id": v.variant_id,
            "mutations": v.mutations[:5] if v.mutations else [],  # Limit mutations shown
            "parent": v.parent_id,
            "generation": v.generation
        }
        variant_info.append(info)
    
    prompt = f"""You are analyzing a scientific paper about enzyme engineering. No PDB IDs were found in the paper, and I need to obtain protein sequences for the enzyme variants described.

Here are the variants found in the paper:
{json.dumps(variant_info, indent=2)}

Please analyze the paper text and:
1. Identify the common name of the enzyme being studied (e.g., "P450 BM3", "cytochrome P450 BM3", "CYP102A1")
2. If possible, extract or find the wild-type sequence
3. Provide any UniProt IDs or accession numbers mentioned

Paper text (first 5000 characters):
{text[:5000]}

Return your response as a JSON object with this structure:
{{
    "enzyme_name": "common name of the enzyme",
    "systematic_name": "systematic name if applicable (e.g., CYP102A1)",
    "uniprot_id": "UniProt ID if found",
    "wild_type_sequence": "sequence if found in paper or if you know it",
    "additional_names": ["list", "of", "alternative", "names"]
}}

If you cannot determine certain fields, set them to null.
"""
    
    try:
        response = model.generate_content(prompt)
        text_response = _extract_text(response).strip()
        
        # Parse JSON response
        if text_response.startswith("```"):
            text_response = text_response.split("```")[1].strip()
            if text_response.startswith("json"):
                text_response = text_response[4:].strip()
            text_response = text_response.split("```")[0].strip()
        
        enzyme_info = json.loads(text_response)
        log.info(f"Gemini extracted enzyme info: {enzyme_info.get('enzyme_name', 'Unknown')}")
        
        sequences = {}
        
        # If Gemini provided a sequence directly, use it
        if enzyme_info.get("wild_type_sequence"):
            # Clean the sequence
            seq = enzyme_info["wild_type_sequence"].upper().replace(" ", "").replace("\n", "")
            # Validate it looks like a protein sequence
            if seq and all(c in "ACDEFGHIKLMNPQRSTVWY*" for c in seq) and len(seq) > 50:
                # Map to the first variant or wild-type
                wt_variant = next((v for v in variants if "WT" in v.variant_id.upper() or v.generation == 0), None)
                if wt_variant:
                    sequences[wt_variant.variant_id] = seq
                else:
                    sequences[variants[0].variant_id] = seq
                log.info(f"Using sequence from Gemini: {len(seq)} residues")
        
        # If no sequence but we have names, try to fetch from UniProt
        if not sequences:
            names_to_try = []
            if enzyme_info.get("enzyme_name"):
                names_to_try.append(enzyme_info["enzyme_name"])
            if enzyme_info.get("systematic_name"):
                names_to_try.append(enzyme_info["systematic_name"])
            if enzyme_info.get("uniprot_id"):
                names_to_try.append(enzyme_info["uniprot_id"])
            if enzyme_info.get("additional_names"):
                names_to_try.extend(enzyme_info["additional_names"])
            
            # Try each name with UniProt
            for name in names_to_try:
                if name:
                    uniprot_seqs = fetch_sequence_by_name(name)
                    if uniprot_seqs:
                        # Map the first sequence to appropriate variant
                        seq = list(uniprot_seqs.values())[0]
                        wt_variant = next((v for v in variants if "WT" in v.variant_id.upper() or v.generation == 0), None)
                        if wt_variant:
                            sequences[wt_variant.variant_id] = seq
                        else:
                            sequences[variants[0].variant_id] = seq
                        log.info(f"Found sequence via UniProt search for '{name}': {len(seq)} residues")
                        break
        
        return sequences
        
    except Exception as e:
        log.warning(f"Failed to extract enzyme info with Gemini: {e}")
        return {}


def fetch_sequence_by_name(enzyme_name: str) -> Dict[str, str]:
    """Fetch protein sequences from UniProt by enzyme name or ID.
    
    Args:
        enzyme_name: Name, ID, or accession of the enzyme
    
    Returns:
        Dict mapping identifiers to sequences
    """
    import requests
    
    clean_name = enzyme_name.strip()
    
    # First try as accession number
    if len(clean_name) <= 10 and (clean_name[0].isalpha() and clean_name[1:].replace("_", "").isalnum()):
        # Looks like a UniProt accession
        url = f"https://rest.uniprot.org/uniprotkb/{clean_name}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                sequence = data.get('sequence', {}).get('value', '')
                if sequence:
                    return {clean_name: sequence}
        except:
            pass
    
    # Try search API
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": f'(protein_name:"{clean_name}" OR gene:"{clean_name}" OR id:"{clean_name}")',
        "format": "json",
        "size": "5",
        "fields": "accession,id,protein_name,gene_names,sequence"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = data.get('results', [])
        sequences = {}
        
        for result in results[:1]:  # Just take the first match
            sequence = result.get('sequence', {}).get('value', '')
            if sequence:
                sequences[clean_name] = sequence
                break
        
        return sequences
        
    except Exception as e:
        log.warning(f"Failed to fetch sequence for '{enzyme_name}': {e}")
        return {}


def _match_variant_ids_with_gemini(
    lineage_variant_ids: List[str], 
    pdb_variant_ids: List[str], 
    model
) -> Dict[str, str]:
    """Use Gemini to match variant IDs that may have slight formatting differences.
    
    Args:
        lineage_variant_ids: List of variant IDs from the lineage
        pdb_variant_ids: List of variant IDs from PDB matching
        model: Gemini model for matching
        
    Returns:
        Dictionary mapping lineage_variant_id -> pdb_variant_id
    """
    if not lineage_variant_ids or not pdb_variant_ids or not model:
        return {}
    
    # If the lists are identical, return direct mapping
    if set(lineage_variant_ids) == set(pdb_variant_ids):
        return {vid: vid for vid in lineage_variant_ids if vid in pdb_variant_ids}
    
    # Use Gemini to match variant IDs that may have formatting differences
    prompt = f"""Match variant IDs between two lists that may have slight formatting differences (whitespace, encoding, etc.).
These represent the same enzyme variants but may be formatted differently.

Lineage variant IDs:
{json.dumps(lineage_variant_ids, indent=2)}

PDB variant IDs:
{json.dumps(pdb_variant_ids, indent=2)}

Match variants that represent the SAME enzyme variant, accounting for:
- Whitespace differences (extra spaces, tabs)
- Character encoding differences
- Minor formatting variations

Return ONLY a JSON object mapping lineage IDs to PDB IDs.
Format: {{"lineage_id": "pdb_id", ...}}
Only include matches you are confident represent the same variant.
Return an empty object {{}} if no matches can be confidently made.
"""
    
    try:
        response = model.generate_content(prompt)
        text = _extract_text(response).strip()
        
        # Parse JSON response
        if text.startswith("```"):
            text = text.split("```")[1].strip()
            if text.startswith("json"):
                text = text[4:].strip()
        
        # Clean up the text
        text = text.strip()
        if not text or text == "{}":
            return {}
        
        matches = json.loads(text)
        log.info(f"Gemini matched {len(matches)} variant IDs for PDB assignment")
        
        # Validate matches
        valid_matches = {}
        for lineage_id, pdb_id in matches.items():
            if lineage_id in lineage_variant_ids and pdb_id in pdb_variant_ids:
                valid_matches[lineage_id] = pdb_id
                log.info(f"Variant ID match: {lineage_id} -> {pdb_id}")
            else:
                log.warning(f"Invalid match ignored: {lineage_id} -> {pdb_id}")
        
        return valid_matches
        
    except Exception as e:
        log.warning(f"Failed to match variant IDs with Gemini: {e}")
        return {}


def match_pdb_to_variants(
    pdb_sequences: Dict[str, str],
    variants: List[Variant],
    lineage_text: str,
    model,
    pdb_id: str = None,
) -> Dict[str, str]:
    """Match PDB chains to variant IDs using LLM analysis of mutations.
    
    Returns a mapping where each variant maps to at most one PDB chain.
    Since all chains from a single PDB typically have the same sequence,
    we match the PDB to a single variant based on context.
    """
    
    if not pdb_sequences or not variants:
        return {}
    
    # Extract context around PDB ID mentions if possible
    context_text = ""
    if pdb_id and lineage_text:
        # Search for PDB ID mentions in the text
        pdb_mentions = []
        text_lower = lineage_text.lower()
        pdb_lower = pdb_id.lower()
        
        # Find all occurrences of the PDB ID
        start = 0
        while True:
            pos = text_lower.find(pdb_lower, start)
            if pos == -1:
                break
            
            # Extract context around the mention (300 chars before, 300 after)
            context_start = max(0, pos - 300)
            context_end = min(len(lineage_text), pos + len(pdb_id) + 300)
            context = lineage_text[context_start:context_end]
            
            # Add ellipsis if truncated
            if context_start > 0:
                context = "..." + context
            if context_end < len(lineage_text):
                context = context + "..."
                
            pdb_mentions.append(context)
            start = pos + 1
        
        if pdb_mentions:
            context_text = "\n\n---\n\n".join(pdb_mentions[:3])  # Use up to 3 mentions
            log.info(f"Found {len(pdb_mentions)} mentions of PDB {pdb_id}")
        else:
            # Fallback to general context if no specific mentions found
            context_text = lineage_text[:2000]
    else:
        # Fallback to general context
        context_text = lineage_text[:2000] if lineage_text else ""
    
    # Get the first chain's sequence as representative (usually all chains have same sequence)
    first_chain = list(pdb_sequences.keys())[0]
    seq_preview = pdb_sequences[first_chain]
    seq_preview = f"{seq_preview[:50]}...{seq_preview[-20:]}" if len(seq_preview) > 70 else seq_preview
    
    # Build a prompt for Gemini to match ONE variant to this PDB
    prompt = f"""Given a PDB structure and enzyme variant information, identify which variant corresponds to this PDB structure.

PDB ID: {pdb_id or "Unknown"}
PDB Sequence (from chain {first_chain}):
{seq_preview}

Variant Information:
{json.dumps([{"id": v.variant_id, "mutations": v.mutations, "parent": v.parent_id, "generation": v.generation} for v in variants], indent=2)}

Context from paper mentioning the PDB:
{context_text}

Please carefully analyze the context to determine:
- Which specific variant was crystallized and deposited as this PDB structure
- Whether the structure represents the starting/parent enzyme or an evolved variant
- Pay attention to phrases describing what the structure shows versus what mutations were made
- Consider the generation number (0 = starting variant, higher = more evolved)

Based on careful analysis of the context, identify which ONE variant this PDB structure represents.
Return ONLY the variant_id as a JSON string.
"""
    
    try:
        response = model.generate_content(prompt)
        text = _extract_text(response).strip()
        
        # Parse JSON response (expecting a single string)
        # Look for JSON code blocks first
        if "```json" in text:
            # Extract content between ```json and ```
            import re
            json_match = re.search(r'```json\s*\n?(.*?)\n?```', text, re.DOTALL)
            if json_match:
                json_content = json_match.group(1).strip()
                try:
                    # Parse as JSON and extract the string value
                    parsed = json.loads(json_content)
                    matched_variant = str(parsed).strip('"\'')
                except:
                    # If JSON parsing fails, try to extract the quoted string
                    quoted_match = re.search(r'"([^"]+)"', json_content)
                    if quoted_match:
                        matched_variant = quoted_match.group(1)
                    else:
                        matched_variant = json_content.strip('"\'')
            else:
                matched_variant = text.strip('"\'')
        elif text.startswith("```"):
            # Handle other code blocks
            text = text.split("```")[1].strip()
            if text.startswith("json"):
                text = text[4:].strip()
            matched_variant = text.strip('"\'')
        else:
            # Look for quoted strings in the response
            import re
            quoted_match = re.search(r'"([^"]+)"', text)
            if quoted_match:
                matched_variant = quoted_match.group(1)
            else:
                # Remove quotes if present
                matched_variant = text.strip('"\'')
        
        log.info(f"Extracted variant name: '{matched_variant}' from response")
        log.info(f"PDB {pdb_id} matched to variant: {matched_variant}")
        
        # Return mapping with all chains pointing to the same variant
        mapping = {}
        if matched_variant:
            # Debug logging
            variant_ids = [v.variant_id for v in variants]
            log.info(f"Looking for variant '{matched_variant}' in lineage variants: {variant_ids}")
            
            # Check if the matched variant exists in the lineage
            found_variant = any(v.variant_id == matched_variant for v in variants)
            log.info(f"Variant '{matched_variant}' found in lineage: {found_variant}")
            
            if found_variant:
                for chain_id in pdb_sequences:
                    mapping[matched_variant] = chain_id
                    log.info(f"Created mapping: {matched_variant} -> {chain_id}")
                    break  # Only use the first chain
            else:
                log.warning(f"Variant '{matched_variant}' not found in lineage variants")
                # Try fuzzy matching
                for variant in variants:
                    if variant.variant_id.strip() == matched_variant.strip():
                        log.info(f"Found fuzzy match: '{variant.variant_id}' == '{matched_variant}'")
                        for chain_id in pdb_sequences:
                            mapping[variant.variant_id] = chain_id
                            log.info(f"Created fuzzy mapping: {variant.variant_id} -> {chain_id}")
                            break
                        break
        else:
            log.warning("No matched variant extracted from response")
        
        log.info(f"Final mapping result: {mapping}")
        return mapping
        
    except Exception as e:
        log.warning(f"Failed to match PDB to variant: {e}")
        # No fallback - return empty if we can't match
        return {}

# === 8. MERGE, VALIDATE & SCORE === ------------------------------------------
"""Glue logic to combine lineage records with sequence blocks and produce a
single tidy pandas DataFrame that downstream code (pipeline / CLI) can write
as CSV or further analyse.

Responsibilities
----------------
1. Merge: outer-join on `variant_id`, preserving every lineage row even if a
   sequence is missing.
2. Generation sanity-check: ensure generation numbers are integers >=0; if
   missing, infer by walking the lineage graph.
3. Confidence: propagate `SequenceBlock.confidence` or compute a simple score
   if only raw sequences are present.
4. DOI column: attach the article DOI to every row so the CSV is self-contained.
"""


# --- 8.1  Generation inference -------------------------------------------------

def _infer_generations(variants: List[Variant]) -> None:
    """Fill in missing `generation` fields by walking parent -> child edges.

    We build a directed graph of variant relationships and assign generation
    numbers by distance from the root(s).  If cycles exist (shouldn't!), they
    are broken arbitrarily and a warning is emitted.
    """
    graph = nx.DiGraph()
    for var in variants:
        graph.add_node(var.variant_id, obj=var)
        if var.parent_id:
            graph.add_edge(var.parent_id, var.variant_id)

    # Detect cycles just in case
    try:
        roots = [n for n, d in graph.in_degree() if d == 0]
        for root in roots:
            for node, depth in nx.single_source_shortest_path_length(graph, root).items():
                var: Variant = graph.nodes[node]["obj"]  # type: ignore[assignment]
                var.generation = depth if var.generation is None else var.generation
    except nx.NetworkXUnfeasible:
        log.warning("Cycle detected in lineage, generation inference skipped")

# --- 8.2  Merge helpers --------------------------------------------------------


def _merge_lineage_and_sequences(
    lineage: List[Variant], seqs: List[SequenceBlock], doi: Optional[str], model=None
) -> pd.DataFrame:
    """Return a tidy DataFrame with one row per variant."""

    # 1. Make DataFrames
    df_lin = pd.DataFrame([
        {
            "variant_id": v.variant_id,
            "parent_id": v.parent_id,
            "generation": v.generation,
            "mutations": ";".join(v.mutations) if v.mutations else None,
            "campaign_id": v.campaign_id,
            "notes": v.notes,
        }
        for v in lineage
    ])

    if seqs:
        df_seq = pd.DataFrame([
            {
                "variant_id": s.variant_id,
                "aa_seq": s.aa_seq,
                "dna_seq": s.dna_seq,
                "seq_confidence": s.confidence,
                "truncated": s.truncated,
                "seq_source": s.metadata.get("source", None) if s.metadata else None,
            }
            for s in seqs
        ])
    else:
        # Create empty DataFrame with correct columns for merging
        df_seq = pd.DataFrame(columns=[
            "variant_id", "aa_seq", "dna_seq", "seq_confidence", "truncated", "seq_source"
        ])
    
    # Log sequence data info
    if len(df_seq) > 0:
        seq_with_aa = (~df_seq['aa_seq'].isna()).sum()
        seq_with_dna = (~df_seq['dna_seq'].isna()).sum()
        log.info(f"Sequence data: {len(df_seq)} entries, {seq_with_aa} with aa_seq, {seq_with_dna} with dna_seq")

    # 2. First try direct merge
    df = pd.merge(df_lin, df_seq, on="variant_id", how="left")
    
    # Log merge results
    merged_aa = (~df['aa_seq'].isna()).sum()
    merged_dna = (~df['dna_seq'].isna()).sum()
    log.info(f"After direct merge: {merged_aa} variants with aa_seq, {merged_dna} with dna_seq")
    
    # 3. If we have unmatched sequences and a model, use Gemini to match
    if model and len(df_seq) > 0 and (df['aa_seq'].isna().any() or df['dna_seq'].isna().any()):
        # Find unmatched entries - consider entries missing if they lack BOTH aa_seq and dna_seq
        missing_seq = df['aa_seq'].isna() & df['dna_seq'].isna()
        unmatched_lineage_ids = df[missing_seq]['variant_id'].tolist()
        
        # Find unmatched sequences
        matched_seq_ids = df[~missing_seq]['variant_id'].tolist()
        unmatched_seqs = df_seq[~df_seq['variant_id'].isin(matched_seq_ids)]
        
        if unmatched_lineage_ids and len(unmatched_seqs) > 0:
            log.info(f"Found {len(unmatched_lineage_ids)} lineage entries without sequences")
            log.info(f"Found {len(unmatched_seqs)} unmatched sequences")
            log.info("Using Gemini to match variants")
            
            # Build prompt for Gemini
            prompt = f"""Match enzyme variant IDs between two lists from the same paper using your best judgment.

These IDs come from different sections of the paper and may use different naming conventions for the same variant.

Lineage variant IDs (need sequences):
{json.dumps(unmatched_lineage_ids)}

Sequence variant IDs (have sequences):
{json.dumps(unmatched_seqs['variant_id'].tolist())}

IMPORTANT MATCHING RULES:
1. Each sequence ID can only be matched to ONE lineage ID (one-to-one mapping)
2. If a lineage ID has additional text after the variant name (like "_something" or other suffixes that are not part of the variant name), it's probably not the exact variant - match the sequence to the best matching variant ID without the suffix
3. A variant with mutations (indicated by mutation codes like letters and numbers after an underscore or space) is a DIFFERENT enzyme from its parent. Do not match mutation variants to their base sequences - they are distinct entities with different sequences due to the mutations.
4. Prioritize exact matches first, then consider matches where the lineage ID contains the sequence ID as a prefix

Only match variants that represent the SAME enzyme, accounting for different naming conventions between sections.

Return ONLY a JSON object mapping lineage IDs to sequence IDs.
Format: {{"lineage_id": "sequence_id", ...}}
Only include matches you are confident represent the same variant.
Each sequence_id should appear at most once in the mapping.

DO NOT include any explanation, reasoning, or text other than the JSON object.
Response must be valid JSON that starts with {{ and ends with }}
"""
            
            try:
                log.info("Sending variant matching request to Gemini...")
                log.debug(f"Prompt length: {len(prompt)} characters")
                
                response = model.generate_content(prompt)
                log.debug(f"Gemini response object: {response}")
                log.debug(f"Response candidates: {getattr(response, 'candidates', 'N/A')}")
                
                text = _extract_text(response).strip()
                log.info(f"Extracted text length: {len(text)}")
                
                if not text:
                    log.error("Gemini returned empty text - API call may have failed")
                    log.error(f"Response object: {response}")
                    if hasattr(response, 'prompt_feedback'):
                        log.error(f"Prompt feedback: {response.prompt_feedback}")
                    raise ValueError("Empty response from Gemini")
                
                log.debug(f"Raw response (first 500 chars): {text[:500]}")
                
                # Parse JSON response
                if text.startswith("```"):
                    text = text.split("```")[1].strip()
                    if text.startswith("json"):
                        text = text[4:].strip()
                
                log.debug(f"Cleaned text for JSON parsing (first 500 chars): {text[:500]}")
                
                if not text.strip():
                    log.error("Text is empty after cleaning")
                    matches = {}
                else:
                    try:
                        matches = json.loads(text)
                        log.info(f"Successfully parsed {len(matches)} matches from Gemini")
                    except json.JSONDecodeError as e:
                        log.error(f"JSON parsing failed: {e}")
                        log.error(f"Full cleaned text: {text}")
                        # Try to extract JSON from within the response
                        import re
                        # First try to find JSON in code blocks
                        code_block_match = re.search(r'```json\s*(\{[^`]*\})\s*```', text, re.DOTALL)
                        if code_block_match:
                            try:
                                matches = json.loads(code_block_match.group(1))
                                log.info(f"Successfully extracted JSON from code block: {len(matches)} matches")
                            except json.JSONDecodeError:
                                log.error("Failed to parse JSON from code block")
                                matches = {}
                        else:
                            # Try to find standalone JSON object (non-greedy, looking for balanced braces)
                            json_match = re.search(r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})', text)
                            if json_match:
                                try:
                                    matches = json.loads(json_match.group(1))
                                    log.info(f"Successfully extracted JSON from response: {len(matches)} matches")
                                except json.JSONDecodeError:
                                    log.error("Failed to extract JSON from response")
                                    matches = {}
                            else:
                                log.error("No JSON object found in response")
                                matches = {}
                
                # Create a mapping of sequence IDs to their data for efficient lookup
                seq_data_map = {row['variant_id']: row for idx, row in unmatched_seqs.iterrows()}
                
                # Apply matches and update variant IDs
                for lineage_id, seq_id in matches.items():
                    if lineage_id in unmatched_lineage_ids and seq_id in seq_data_map:
                        # Get the sequence data
                        seq_data = seq_data_map[seq_id]
                        
                        # Update the row with the matched sequence ID and data
                        mask = df['variant_id'] == lineage_id
                        if mask.any():
                            # Update variant_id to use the sequence variant name
                            df.loc[mask, 'variant_id'] = seq_id
                            
                            # Update parent_id if it matches any of the mapped lineage IDs
                            parent_mask = df['parent_id'] == lineage_id
                            if parent_mask.any():
                                df.loc[parent_mask, 'parent_id'] = seq_id
                            
                            # Update sequence data
                            # For pandas Series from iterrows(), use proper indexing
                            aa_seq_val = seq_data['aa_seq'] if 'aa_seq' in seq_data else None
                            dna_seq_val = seq_data['dna_seq'] if 'dna_seq' in seq_data else None
                            
                            # Always update sequence fields to preserve DNA even when aa_seq is null
                            df.loc[mask, 'aa_seq'] = aa_seq_val
                            df.loc[mask, 'dna_seq'] = dna_seq_val
                                
                            df.loc[mask, 'seq_confidence'] = seq_data.get('seq_confidence', None)
                            df.loc[mask, 'truncated'] = seq_data.get('truncated', False)
                            
                            # Log sequence info - check both aa_seq and dna_seq
                            aa_len = len(seq_data['aa_seq']) if pd.notna(seq_data.get('aa_seq')) and seq_data.get('aa_seq') else 0
                            dna_len = len(seq_data['dna_seq']) if pd.notna(seq_data.get('dna_seq')) and seq_data.get('dna_seq') else 0
                            log.info(f"Matched {lineage_id} -> {seq_id} (aa_seq: {aa_len} chars, dna_seq: {dna_len} chars)")
                
                # Update any remaining parent_id references to matched variants
                for lineage_id, seq_id in matches.items():
                    parent_mask = df['parent_id'] == lineage_id
                    if parent_mask.any():
                        df.loc[parent_mask, 'parent_id'] = seq_id
                
                # Log final state - count variants with any sequence (aa or dna)
                aa_count = (~df['aa_seq'].isna()).sum()
                dna_count = (~df['dna_seq'].isna()).sum()
                any_seq_count = (~(df['aa_seq'].isna() & df['dna_seq'].isna())).sum()
                log.info(f"After Gemini matching: {any_seq_count}/{len(df)} variants have sequences (aa: {aa_count}, dna: {dna_count})")
                
            except Exception as e:
                log.warning(f"Failed to match variants using Gemini: {e}")

    # 4. If generation missing, try inference
    if df["generation"].isna().any():
        _infer_generations(lineage)
        # Need to update the generations based on the potentially updated variant IDs
        gen_map = {v.variant_id: v.generation for v in lineage}
        # Also create a map for any variant IDs that were replaced
        for idx, row in df.iterrows():
            variant_id = row['variant_id']
            if variant_id in gen_map:
                df.at[idx, 'generation'] = gen_map[variant_id]

    # 5. Attach DOI column
    df["doi"] = doi

    # 6. Sort by campaign_id, then generation
    df = df.sort_values(["campaign_id", "generation"], kind="mergesort")

    # 7. Log final state
    aa_count = (~df['aa_seq'].isna()).sum()
    dna_count = (~df['dna_seq'].isna()).sum()
    any_seq_count = (~(df['aa_seq'].isna() & df['dna_seq'].isna())).sum()
    log.info(f"Final result: {len(df)} variants, {any_seq_count} with sequences (aa: {aa_count}, dna: {dna_count})")

    return df

# --- 8.3  Public API -----------------------------------------------------------

def merge_and_score(
    lineage: List[Variant],
    seqs: List[SequenceBlock],
    doi: Optional[str] = None,
    model=None,
) -> pd.DataFrame:
    """Merge lineage and sequence data into a single DataFrame.
    
    Args:
        lineage: List of Variant objects from lineage extraction
        seqs: List of SequenceBlock objects from sequence extraction
        doi: DOI of the paper for provenance
        model: Gemini model for smart matching (optional)
    
    Returns:
        DataFrame with merged lineage and sequence data
    """
    if not lineage:
        raise ValueError("merge_and_score(): `lineage` list is empty; nothing to merge")

    df = _merge_lineage_and_sequences(lineage, seqs, doi, model)

    # Warn if many sequences are missing
    missing_rate = df["aa_seq"].isna().mean() if "aa_seq" in df else 1.0
    if missing_rate > 0.5:
        log.warning(">50%% of variants lack sequences (%d / %d)", df["aa_seq"].isna().sum(), len(df))

    return df

# -------------------------------------------------------------------- end 8 ---

# === 9. PIPELINE ORCHESTRATOR === --------------------------------------------
"""High-level function that ties together PDF parsing, LLM calls, merging, and
CSV export.  This is what both the CLI (Section 10) and other Python callers
should invoke.

**New behaviour (June 2025)** - The lineage table is now written to disk *before*
sequence extraction begins so that users keep partial results even if the
LLM stalls on the longer sequence prompt.  The same `--output` path is used;
we first save the lineage-only CSV, then overwrite it later with the merged
(final) DataFrame.
"""

import time
from pathlib import Path
from typing import Union
import pandas as pd


def _lineage_to_dataframe(lineage: list[Variant]) -> pd.DataFrame:
    """Convert a list[Variant] to a tidy DataFrame (helper for early dump)."""
    return pd.DataFrame(
        {
            "variant_id": [v.variant_id for v in lineage],
            "parent_id":  [v.parent_id for v in lineage],
            "generation": [v.generation for v in lineage],
            "mutations":  [";".join(v.mutations) if v.mutations else None for v in lineage],
            "campaign_id": [v.campaign_id for v in lineage],
            "notes":      [v.notes for v in lineage],
        }
    )


def run_pipeline(
    manuscript: Union[str, Path],
    si: Optional[Union[str, Path]] = None,
    output_csv: Optional[Union[str, Path]] = None,
    *,
    debug_dir: str | Path | None = None,
) -> pd.DataFrame:
    """Execute the end-to-end extraction pipeline.

    Parameters
    ----------
    manuscript : str | Path
        Path to the main PDF file.
    si : str | Path | None, optional
        Path to the Supplementary Information PDF, if available.
    output_csv : str | Path | None, optional
        If provided, **both** the early lineage table *and* the final merged
        table will be written to this location (the final write overwrites
        the first).

    Returns
    -------
    pandas.DataFrame
        One row per variant with lineage, sequences, and provenance.
    """

    t0 = time.perf_counter()
    manuscript = Path(manuscript)
    si_path = Path(si) if si else None

    # 1. Prepare raw text ------------------------------------------------------
    # Always load both caption text (for identification) and full text (for extraction)
    pdf_paths = [p for p in (manuscript, si_path) if p]
    caption_text = limited_caption_concat(*pdf_paths)
    full_text = limited_concat(*pdf_paths)
    
    # Also load separate texts for manuscript and SI
    manuscript_text = limited_concat(manuscript) if manuscript else None
    si_text = limited_concat(si_path) if si_path else None
    
    log.info("Loaded %d chars of captions for identification and %d chars of full text for extraction", 
             len(caption_text), len(full_text))
    if manuscript_text:
        log.info("Loaded %d chars from manuscript", len(manuscript_text))
    if si_text:
        log.info("Loaded %d chars from SI", len(si_text))

    # 2. Connect to Gemini -----------------------------------------------------
    model = get_model()

    # 3. Extract lineage (Section 6) ------------------------------------------
    lineage, campaigns = get_lineage(
        caption_text, full_text, model, 
        pdf_paths=pdf_paths, 
        debug_dir=debug_dir,
        manuscript_text=manuscript_text,
        si_text=si_text
    )

    if not lineage:
        raise RuntimeError("Pipeline aborted: failed to extract any lineage data")
    
    # Save campaigns info if debug_dir provided
    if debug_dir and campaigns:
        campaigns_file = Path(debug_dir) / "campaigns.json"
        campaigns_data = [
            {
                "campaign_id": c.campaign_id,
                "campaign_name": c.campaign_name,
                "description": c.description,
                "model_substrate": c.model_substrate,
                "model_product": c.model_product,
                "substrate_id": c.substrate_id,
                "product_id": c.product_id,
                "data_locations": c.data_locations,
                "notes": c.notes
            }
            for c in campaigns
        ]
        _dump(json.dumps(campaigns_data, indent=2), campaigns_file)
        log.info(f"Saved {len(campaigns)} campaigns to {campaigns_file}")

    # 3a. EARLY SAVE  -------------------------------------------------------------
    if output_csv:
        early_df = _lineage_to_dataframe(lineage)
        output_csv_path = Path(output_csv)
        # Save lineage-only data with specific filename
        lineage_path = output_csv_path.parent / "enzyme_lineage_name.csv"
        early_df.to_csv(lineage_path, index=False)
        log.info(
            "Saved lineage-only CSV -> %s",
            lineage_path,
        )

    # 4. Extract sequences (Section 7) ----------------------------------------
    sequences = get_sequences(full_text, model, pdf_paths=pdf_paths, debug_dir=debug_dir, lineage_variants=lineage)
    
    # 4a. First try to merge extracted sequences with lineage using Gemini matching
    # This allows fuzzy matching of complex variant IDs before external lookups
    doi = extract_doi(manuscript)
    df_merged = merge_and_score(lineage, sequences, doi, model)
    
    # 4b. Check if ALL variants are missing sequences after merging
    # Only try external sources if no sequences were successfully matched
    all_missing_sequences = True
    if 'aa_seq' in df_merged.columns or 'dna_seq' in df_merged.columns:
        for _, row in df_merged.iterrows():
            has_aa = pd.notna(row.get('aa_seq'))
            has_dna = pd.notna(row.get('dna_seq'))
            if has_aa or has_dna:
                all_missing_sequences = False
                break
    
    if all_missing_sequences:
        MIN_PROTEIN_LENGTH = 50  # Most proteins are >50 AA
        MIN_DNA_LENGTH = 150  # DNA sequences should be >150 nt
        log.info("No full-length sequences found in paper (only partial sequences < %d AA or < %d nt), attempting PDB extraction...", 
                 MIN_PROTEIN_LENGTH, MIN_DNA_LENGTH)
        
        # Extract PDB IDs from all PDFs
        pdb_ids = []
        for pdf_path in pdf_paths:
            pdb_ids.extend(extract_pdb_ids(pdf_path))
        
        if pdb_ids:
            log.info(f"Found PDB IDs: {pdb_ids}")
            
            # Try each PDB ID until we get sequences
            for pdb_id in pdb_ids:
                pdb_sequences = fetch_pdb_sequences(pdb_id)
                
                if pdb_sequences:
                    # Match PDB chains to variants
                    variant_to_chain = match_pdb_to_variants(
                        pdb_sequences, lineage, full_text, model, pdb_id
                    )
                    
                    log.info(f"PDB matching result: {variant_to_chain}")
                    log.info(f"Available PDB sequences: {list(pdb_sequences.keys())}")
                    log.info(f"Lineage variants: {[v.variant_id for v in lineage]}")
                    
                    # Convert to SequenceBlock objects
                    pdb_seq_blocks = []
                    
                    # Use Gemini-based matching for robust variant ID comparison
                    if variant_to_chain and model:
                        # Create a mapping using Gemini for robust string matching
                        gemini_mapping = _match_variant_ids_with_gemini(
                            lineage_variant_ids=[v.variant_id for v in lineage],
                            pdb_variant_ids=list(variant_to_chain.keys()),
                            model=model
                        )
                        
                        for variant in lineage:
                            log.info(f"Processing variant: {variant.variant_id}")
                            
                            # Try direct match first
                            chain_id = variant_to_chain.get(variant.variant_id)
                            log.info(f"Direct match for {variant.variant_id}: {chain_id}")
                            
                            # If no direct match, try Gemini-based matching
                            if not chain_id:
                                matched_pdb_variant = gemini_mapping.get(variant.variant_id)
                                log.info(f"Gemini match for {variant.variant_id}: {matched_pdb_variant}")
                                if matched_pdb_variant:
                                    chain_id = variant_to_chain.get(matched_pdb_variant)
                                    log.info(f"Chain ID from Gemini match: {chain_id}")
                            
                            if chain_id and chain_id in pdb_sequences:
                                seq_length = len(pdb_sequences[chain_id])
                                log.info(f"Creating sequence block for {variant.variant_id} with {seq_length} residues from chain {chain_id}")
                                seq_block = SequenceBlock(
                                    variant_id=variant.variant_id,
                                    aa_seq=pdb_sequences[chain_id],
                                    dna_seq=None,
                                    confidence=1.0,  # High confidence for PDB sequences
                                    truncated=False,
                                    metadata={"source": "PDB", "pdb_id": pdb_id, "chain": chain_id}
                                )
                                pdb_seq_blocks.append(seq_block)
                                log.info(f"Added PDB sequence for {variant.variant_id} from {pdb_id}:{chain_id}")
                            else:
                                log.warning(f"No chain_id found for variant {variant.variant_id} or chain not in sequences")
                    else:
                        # Fallback to direct matching if no model or no matches
                        for variant in lineage:
                            if variant.variant_id in variant_to_chain:
                                chain_id = variant_to_chain[variant.variant_id]
                                if chain_id in pdb_sequences:
                                    seq_block = SequenceBlock(
                                        variant_id=variant.variant_id,
                                        aa_seq=pdb_sequences[chain_id],
                                        dna_seq=None,
                                        confidence=1.0,  # High confidence for PDB sequences
                                        truncated=False,
                                        metadata={"source": "PDB", "pdb_id": pdb_id, "chain": chain_id}
                                    )
                                    pdb_seq_blocks.append(seq_block)
                                    log.info(f"Added PDB sequence for {variant.variant_id} from {pdb_id}:{chain_id}")
                    
                    log.info(f"PDB sequence blocks created: {len(pdb_seq_blocks)}")
                    
                    if pdb_seq_blocks:
                        # Update the dataframe with PDB sequences
                        for seq_block in pdb_seq_blocks:
                            mask = df_merged['variant_id'] == seq_block.variant_id
                            if mask.any():
                                df_merged.loc[mask, 'aa_seq'] = seq_block.aa_seq
                                df_merged.loc[mask, 'seq_confidence'] = seq_block.confidence
                                df_merged.loc[mask, 'seq_source'] = seq_block.metadata.get('source', 'PDB')
                                log.info(f"Updated dataframe with sequence for {seq_block.variant_id}")
                            else:
                                log.warning(f"No matching row in dataframe for variant {seq_block.variant_id}")
                        log.info(f"Successfully extracted {len(pdb_seq_blocks)} sequences from PDB {pdb_id}")
                        break
                    else:
                        log.warning(f"No PDB sequence blocks were created for {pdb_id}")
                else:
                    log.warning(f"No sequences found in PDB {pdb_id}")
        else:
            log.warning("No PDB IDs found in paper")
            
        # 4c. If still no sequences after PDB, try Gemini extraction as last resort
        # Re-check if all variants are still missing sequences
        still_all_missing = True
        for _, row in df_merged.iterrows():
            if pd.notna(row.get('aa_seq')) or pd.notna(row.get('dna_seq')):
                still_all_missing = False
                break
        
        if still_all_missing:
            log.info("No sequences from PDB, attempting Gemini-based extraction...")
            
            gemini_sequences = extract_enzyme_info_with_gemini(full_text, lineage, model)
            
            if gemini_sequences:
                # Convert to SequenceBlock objects
                gemini_seq_blocks = []
                for variant_id, seq in gemini_sequences.items():
                    # Find the matching variant
                    variant = next((v for v in lineage if v.variant_id == variant_id), None)
                    if variant:
                        seq_block = SequenceBlock(
                            variant_id=variant.variant_id,
                            aa_seq=seq,
                            dna_seq=None,
                            confidence=0.9,  # High confidence but slightly lower than PDB
                            truncated=False,
                            metadata={"source": "Gemini/UniProt"}
                        )
                        gemini_seq_blocks.append(seq_block)
                        log.info(f"Added sequence for {variant.variant_id} via Gemini/UniProt: {len(seq)} residues")
                
                if gemini_seq_blocks:
                    # Update the dataframe with Gemini/UniProt sequences
                    for seq_block in gemini_seq_blocks:
                        mask = df_merged['variant_id'] == seq_block.variant_id
                        if mask.any():
                            df_merged.loc[mask, 'aa_seq'] = seq_block.aa_seq
                            df_merged.loc[mask, 'seq_confidence'] = seq_block.confidence
                            df_merged.loc[mask, 'seq_source'] = seq_block.metadata.get('source', 'Gemini/UniProt')
                    log.info(f"Successfully extracted {len(gemini_seq_blocks)} sequences via Gemini")
            else:
                log.warning("Failed to extract sequences via Gemini")

    # 5. Use the merged dataframe (already merged above)
    df_final = df_merged

    # 6. Write FINAL CSV -------------------------------------------------------
    if output_csv:
        output_csv_path = Path(output_csv)
        # Save final data with sequences using same filename (overwrites lineage-only)
        sequence_path = output_csv_path.parent / "enzyme_lineage_data.csv"
        
        # Save the final CSV
        df_final.to_csv(sequence_path, index=False)
        
        # Log summary statistics
        seq_count = (~df_final['aa_seq'].isna()).sum() if 'aa_seq' in df_final else 0
        log.info(
            "Saved final CSV -> %s (%.1f kB, %d variants, %d with sequences)",
            sequence_path,
            sequence_path.stat().st_size / 1024,
            len(df_final),
            seq_count
        )

    log.info(
        "Pipeline finished in %.2f s (variants: %d)",
        time.perf_counter() - t0,
        len(df_final),
    )
    return df_final

# -------------------------------------------------------------------- end 9 ---

# === 10. CLI ENTRYPOINT === ----------------------------------------------
"""Simple argparse wrapper so the script can be run from the command line

Example:

    python enzyme_lineage_extractor.py \
        --manuscript paper.pdf \
        --si supp.pdf \
        --output lineage.csv \
        --captions-only -v
"""

import argparse
import logging
from typing import List, Optional


# -- 10.1  Argument parser ----------------------------------------------------

def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="enzyme_lineage_extractor",
        description="Extract enzyme variant lineage and sequences from PDFs using Google Gemini",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--manuscript", required=True, help="Path to main manuscript PDF")
    p.add_argument("--si", help="Path to Supplementary Information PDF")
    p.add_argument("-o", "--output", help="CSV file for extracted data")
    p.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity; repeat (-vv) for DEBUG logging",
    )
    p.add_argument(
    "--debug-dir",
    metavar="DIR",
    help="Write ALL intermediate artefacts (captions, prompts, raw Gemini replies) to DIR",
    )
    return p


# -- 10.2  main() -------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> None:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    # Configure logging early so everything respects the chosen level.
    level = logging.DEBUG if args.verbose >= 2 else logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    run_pipeline(
        manuscript=args.manuscript,
        si=args.si,
        output_csv=args.output,
        debug_dir=args.debug_dir,
    )


if __name__ == "__main__":
    main()

# -------------------------------------------------------------------- end 10 ---

