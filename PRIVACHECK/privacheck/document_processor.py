from io import BytesIO
from pathlib import Path
import fitz
from docx import Document

def extract_text(filename: str, content: bytes) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        doc = fitz.open(stream=content, filetype="pdf")
        pages = []
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text")
            if text.strip():
                pages.append(f"\n[Page {i}]\n{text}")
        result = "\n".join(pages)
    elif ext == ".docx":
        doc = Document(BytesIO(content))
        result = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        for table in doc.tables:
            for row in table.rows:
                result += "\n" + " | ".join(cell.text for cell in row.cells)
    elif ext == ".txt":
        result = content.decode("utf-8", errors="replace")
    else:
        raise ValueError("Unsupported format. Please use PDF, DOCX or TXT.")
    result = "\n".join(line.strip() for line in result.splitlines() if line.strip())
    if not result.strip():
        raise ValueError("No readable text found. The PDF may be scanned; OCR is not included in this version.")
    return result
