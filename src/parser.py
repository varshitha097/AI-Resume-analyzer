
from pathlib import Path
from typing import Tuple, Dict
from .cleaner import normalize_whitespace


def _extract_pdf_pymupdf(path: Path) -> str:
    try:
        import fitz  # PyMuPDF
    except Exception:
        return ""
    chunks = []
    try:
        with fitz.open(str(path)) as doc:
            for page in doc:
                # blocks mode keeps columns slightly better than raw text for many resumes
                text = page.get_text("text") or ""
                chunks.append(text)
    except Exception:
        return ""
    return "\n".join(chunks)


def _extract_pdf_pdfplumber(path: Path) -> str:
    try:
        import pdfplumber
    except Exception:
        return ""
    chunks = []
    try:
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
                chunks.append(text)
    except Exception:
        return ""
    return "\n".join(chunks)


def _extract_pdf_ocr(path: Path) -> str:
    """Optional OCR fallback for scanned resumes. Requires poppler + tesseract installed."""
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except Exception:
        return ""
    try:
        pages = convert_from_path(str(path), dpi=220)
        return "\n".join(pytesseract.image_to_string(page) for page in pages)
    except Exception:
        return ""


def _extract_docx(path: Path) -> str:
    try:
        from docx import Document
    except Exception:
        return ""
    try:
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception:
        return ""


def extract_text_from_file(file_path: str) -> Tuple[str, Dict[str, str]]:
    """Extract text from PDF/TXT/DOCX with fallbacks and return metadata."""
    path = Path(file_path)
    suffix = path.suffix.lower()
    meta = {"file_name": path.name, "parser_used": "", "ocr_used": "false"}
    text = ""

    if suffix == ".pdf":
        text = _extract_pdf_pymupdf(path)
        meta["parser_used"] = "PyMuPDF"
        # If extraction is too small, try pdfplumber; columns/tables sometimes work better there.
        if len(text.strip()) < 150:
            alt = _extract_pdf_pdfplumber(path)
            if len(alt.strip()) > len(text.strip()):
                text = alt
                meta["parser_used"] = "pdfplumber"
        # OCR fallback for scanned resumes.
        if len(text.strip()) < 80:
            ocr_text = _extract_pdf_ocr(path)
            if len(ocr_text.strip()) > len(text.strip()):
                text = ocr_text
                meta["parser_used"] = "OCR"
                meta["ocr_used"] = "true"
    elif suffix == ".txt":
        text = path.read_text(encoding="utf-8", errors="ignore")
        meta["parser_used"] = "plain_text"
    elif suffix == ".docx":
        text = _extract_docx(path)
        meta["parser_used"] = "python-docx"
    else:
        # Best effort for unknown files
        text = path.read_text(encoding="utf-8", errors="ignore")
        meta["parser_used"] = "best_effort_text"

    return normalize_whitespace(text), meta
