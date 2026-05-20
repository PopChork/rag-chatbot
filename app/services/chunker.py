from app.config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_pages(
    pages,
    filename: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None
):
    chunk_size = chunk_size or CHUNK_SIZE
    chunk_overlap = chunk_overlap or CHUNK_OVERLAP

    chunks = []

    for page in pages:
        text = clean_text(page["text"])
        page_num = page["page"]

        start = 0
        chunk_index = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "filename": filename,
                    "page": page_num,
                    "chunk_index": chunk_index,
                    "text": chunk_text
                })

            start += chunk_size - chunk_overlap
            chunk_index += 1

    return chunks


def clean_text(text: str):
    return " ".join(text.split())