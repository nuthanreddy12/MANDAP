import pymupdf
from typing import Dict, Any, List

def extract_pdf_content(file_bytes: bytes) -> Dict[str, Any]:
    """
    Extracts text and layout data from PDF bytes using PyMuPDF.
    Preserves page numbers, source snippets, and detects scanned/empty documents.
    """
    doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    page_count = len(doc)
    pages: List[Dict[str, Any]] = []
    full_text_parts: List[str] = []
    total_chars = 0

    for i in range(page_count):
        page = doc[i]
        text = page.get_text("text").strip()
        total_chars += len(text)
        full_text_parts.append(f"--- PAGE {i + 1} ---\n{text}")
        pages.append({
            "page_number": i + 1,
            "text": text,
            "char_count": len(text),
        })

    # Scanned detection heuristic: average < 50 chars per page
    avg_chars = total_chars / page_count if page_count > 0 else 0
    is_scanned = avg_chars < 50 or total_chars < 80

    rendered_images: List[bytes] = []
    if is_scanned and page_count > 0:
        # Render first up to 3 pages to PNG for multimodal/OCR fallback
        for i in range(min(page_count, 3)):
            pix = doc[i].get_pixmap(dpi=150)
            rendered_images.append(pix.tobytes("png"))

    doc.close()

    return {
        "page_count": page_count,
        "is_scanned": is_scanned,
        "total_chars": total_chars,
        "pages": pages,
        "full_text": "\n\n".join(full_text_parts),
        "rendered_images": rendered_images,
    }
