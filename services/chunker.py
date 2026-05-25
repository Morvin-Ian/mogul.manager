"""
Recursive character-level text splitter.
Splits at natural language boundaries (paragraphs → sentences → words)
with configurable overlap so no context is lost between chunks.
"""
from __future__ import annotations

_SEPARATORS = ["\n\n", "\n", ". ", "! ", "? ", ", ", " ", ""]


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split *text* into chunks of at most *chunk_size* chars with *overlap* chars of carry-over."""
    if not text.strip():
        return []
    return _split(text.strip(), chunk_size, overlap, _SEPARATORS)


def _split(text: str, chunk_size: int, overlap: int, separators: list[str]) -> list[str]:
    if len(text) <= chunk_size:
        return [text]

    # Find the best separator present in this text
    chosen_sep = ""
    chosen_idx = len(separators) - 1
    for i, sep in enumerate(separators):
        if sep and sep in text:
            chosen_sep = sep
            chosen_idx = i
            break

    if not chosen_sep:
        # Hard-split fallback
        step = max(chunk_size - overlap, 1)
        return [text[i : i + chunk_size].strip() for i in range(0, len(text), step) if text[i : i + chunk_size].strip()]

    pieces = text.split(chosen_sep)
    result: list[str] = []
    current = ""

    for piece in pieces:
        candidate = (current + chosen_sep + piece).lstrip() if current else piece
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                result.append(current.strip())
                tail = current[-overlap:].strip() if overlap else ""
                current = (tail + " " + piece.strip()).strip() if tail else piece.strip()
            else:
                # piece itself exceeds chunk_size — recurse with finer separators
                sub = _split(piece, chunk_size, overlap, separators[chosen_idx + 1 :])
                result.extend(sub)
                current = ""

    if current:
        result.append(current.strip())

    return [c for c in result if c]
