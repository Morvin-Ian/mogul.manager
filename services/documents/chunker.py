from __future__ import annotations

import re

_SEPARATORS = ["\n\n", "\n", ". ", "! ", "? ", ", ", " ", ""]

_HEADING_RE = re.compile(r"^(#{1,6}\s+|==+\s*$|---+\s*$|__+\s*$)", re.MULTILINE)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    if not text.strip():
        return []

    sections = _split_at_headings(text)
    if len(sections) > 1:
        if all(len(s) <= chunk_size for s in sections):
            return sections
        result: list[str] = []
        for s in sections:
            if len(s) <= chunk_size:
                result.append(s.strip())
            else:
                result.extend(_split(s.strip(), chunk_size, overlap, _SEPARATORS))
        return [r for r in result if r]

    return _split(text.strip(), chunk_size, overlap, _SEPARATORS)


def _split_at_headings(text: str) -> list[str]:
    matches = list(_HEADING_RE.finditer(text))
    if not matches:
        return [text]

    sections: list[str] = []
    prev_end = 0
    for m in matches:
        if m.start() > prev_end:
            sections.append(text[prev_end : m.start()].strip())
        prev_end = m.start()
    if prev_end < len(text):
        sections.append(text[prev_end:].strip())
    return [s for s in sections if s]


def _split(
    text: str, chunk_size: int, overlap: int, separators: list[str]
) -> list[str]:
    if len(text) <= chunk_size:
        return [text]

    chosen_sep = ""
    chosen_idx = len(separators) - 1
    for i, sep in enumerate(separators):
        if sep and sep in text:
            chosen_sep = sep
            chosen_idx = i
            break

    if not chosen_sep:
        step = max(chunk_size - overlap, 1)
        return [
            text[i : i + chunk_size].strip()
            for i in range(0, len(text), step)
            if text[i : i + chunk_size].strip()
        ]

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
                current = (
                    (tail + " " + piece.strip()).strip() if tail else piece.strip()
                )
            else:
                sub = _split(piece, chunk_size, overlap, separators[chosen_idx + 1 :])
                result.extend(sub)
                current = ""

    if current:
        result.append(current.strip())

    return [c for c in result if c]
