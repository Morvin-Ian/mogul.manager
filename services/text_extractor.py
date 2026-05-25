"""
Text extraction from PDF, DOCX, TXT, and CSV files.
Automatically falls back to OCR for scanned PDFs when pytesseract is available.
"""
from __future__ import annotations

import csv
import io
import logging
import re

import pdfplumber
from docx import Document as DocxDoc
from starlette.concurrency import run_in_threadpool

try:
    import pytesseract
    from pdf2image import convert_from_bytes
    _OCR_AVAILABLE = True
except ImportError:
    _OCR_AVAILABLE = False

logger = logging.getLogger(__name__)


async def extract_text(content: bytes, file_type: str) -> tuple[str, dict]:
    """Return (text, metadata). metadata keys: word_count, page_count."""
    ft = file_type.lower()
    if ft == "pdf":
        return await run_in_threadpool(_extract_pdf, content)
    if ft == "docx":
        return await run_in_threadpool(_extract_docx, content)
    if ft == "txt":
        return _extract_txt(content), {}
    if ft == "csv":
        return _extract_csv(content), {}
    raise ValueError(f"Unsupported file type: {file_type}")


# ── PDF ────────────────────────────────────────────────────────────────────────

def _extract_pdf(content: bytes) -> tuple[str, dict]:
    pages: list[str] = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        page_count = len(pdf.pages)
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text)

    full_text = "\n\n".join(pages)

    # Scanned PDF fallback: if extracted text is suspiciously short
    if len(full_text.strip()) < 100 and page_count > 0:
        ocr_text = _try_ocr(content)
        if ocr_text:
            full_text = ocr_text
            logger.info("Used OCR for scanned PDF")

    full_text = _clean_text(full_text)
    return full_text, {"page_count": page_count, "word_count": len(full_text.split())}


def _try_ocr(content: bytes) -> str:
    """Optional OCR via pytesseract + pdf2image. Returns empty string when unavailable."""
    if not _OCR_AVAILABLE:
        logger.warning("OCR not available — install pytesseract and pdf2image for scanned PDF support")
        return ""
    try:
        images = convert_from_bytes(content, dpi=200)
        return "\n\n".join(pytesseract.image_to_string(img) for img in images)
    except Exception as e:
        logger.warning("OCR failed: %s", e)
        return ""


# ── DOCX ───────────────────────────────────────────────────────────────────────

def _extract_docx(content: bytes) -> tuple[str, dict]:
    doc = DocxDoc(io.BytesIO(content))
    parts: list[str] = []

    for para in doc.paragraphs:
        if para.text.strip():
            parts.append(para.text.strip())

    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(c.text.strip() for c in row.cells if c.text.strip())
            if row_text:
                parts.append(row_text)

    full_text = _clean_text("\n\n".join(parts))
    return full_text, {"word_count": len(full_text.split()), "page_count": None}


# ── TXT ────────────────────────────────────────────────────────────────────────

def _extract_txt(content: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            return _clean_text(content.decode(encoding))
        except UnicodeDecodeError:
            continue
    raise RuntimeError("Could not decode text file")


# ── CSV ────────────────────────────────────────────────────────────────────────

def _extract_csv(content: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            raw = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise RuntimeError("Could not decode CSV file")

    reader = csv.DictReader(io.StringIO(raw))
    rows = list(reader)
    headers = list(reader.fieldnames or [])

    lines = [f"Columns: {', '.join(headers)}", ""]
    for row in rows[:500]:
        line = " | ".join(f"{k}: {v}" for k, v in row.items() if v and v.strip())
        if line:
            lines.append(line)

    if len(rows) > 500:
        lines.append(f"[...{len(rows) - 500} more rows not shown]")

    return "\n".join(lines)


# ── Shared ─────────────────────────────────────────────────────────────────────

def _clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()
