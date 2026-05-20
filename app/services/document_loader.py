from io import BytesIO
from pypdf import PdfReader


def extract_document_text(file_bytes: bytes, filename: str):
    if filename.endswith(".pdf"):
        return extract_pdf_text(file_bytes)

    if filename.endswith(".txt"):
        text = file_bytes.decode("utf-8", errors="ignore")
        return [{"page": 1, "text": text}]

    raise ValueError("Unsupported file type.")


def extract_pdf_text(file_bytes: bytes):
    reader = PdfReader(BytesIO(file_bytes))
    pages = []

    for page_index, page in enumerate(reader.pages):
        text = page.extract_text() or ""

        if text.strip():
            pages.append({
                "page": page_index + 1,
                "text": text
            })

    return pages