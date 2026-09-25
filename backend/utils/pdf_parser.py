"""
HireScope Backend — utils/pdf_parser.py
Extract plain text from a PDF file using PyPDF2.
"""

import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract all text from PDF bytes.

    Always returns a string (never None).
    """

    try:
        import PyPDF2

        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        pages = []

        for page in reader.pages:
            try:
                text = page.extract_text()
                if text:
                    pages.append(text.strip())
            except Exception:
                continue  # skip bad pages safely

        return "\n\n".join(pages) if pages else ""

    except ImportError:
        print("[pdf_parser] PyPDF2 not installed. Run: pip install PyPDF2")
        return ""

    except Exception as e:
        print(f"[pdf_parser] Error reading PDF: {e}")
        return ""   # ✅ NEVER return None


def extract_text_from_pdf_path(path: str) -> str:
    """
    Read PDF from file path and extract text.
    Always returns string.
    """

    try:
        with open(path, "rb") as f:
            return extract_text_from_pdf(f.read())

    except Exception as e:
        print(f"[pdf_parser] Could not open file {path}: {e}")
        return ""   # ✅ NEVER return None