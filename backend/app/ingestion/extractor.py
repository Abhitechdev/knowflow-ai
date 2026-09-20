import csv
import io
import logging
from typing import Any

from app.ingestion.cleaner import clean_text, detect_section_heading

logger = logging.getLogger(__name__)


class DocumentExtractor:
    """Extracts structured text from supported file types (PDF, DOCX, TXT, MD, CSV) with page preservation."""

    @staticmethod
    def extract(file_bytes: bytes, file_extension: str) -> list[dict[str, Any]]:
        """Extracts content as a list of pages/sections.
        Each item is: {"page_number": int, "text": str, "section_heading": str}
        """
        ext = file_extension.lower().lstrip(".")
        if ext == "pdf":
            return DocumentExtractor._extract_pdf(file_bytes)
        elif ext in ("docx", "doc"):
            return DocumentExtractor._extract_docx(file_bytes)
        elif ext in ("txt", "log"):
            return DocumentExtractor._extract_txt(file_bytes)
        elif ext == "md":
            return DocumentExtractor._extract_md(file_bytes)
        elif ext == "csv":
            return DocumentExtractor._extract_csv(file_bytes)
        else:
            raise ValueError(f"Unsupported file extension: .{ext}")

    @staticmethod
    def _extract_pdf(file_bytes: bytes) -> list[dict[str, Any]]:
        import pypdf
        pages = []
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        total_pages = len(reader.pages)
        current_heading = "General"

        for page_idx in range(total_pages):
            page_num = page_idx + 1
            try:
                page_obj = reader.pages[page_idx]
                raw_text = page_obj.extract_text() or ""
                cleaned = clean_text(raw_text)
                if cleaned:
                    heading = detect_section_heading(cleaned)
                    if heading != "General":
                        current_heading = heading
                    pages.append({
                        "page_number": page_num,
                        "text": cleaned,
                        "section_heading": current_heading,
                    })
                else:
                    # Keep empty page placeholder if text extraction yielded no chars
                    pages.append({
                        "page_number": page_num,
                        "text": "",
                        "section_heading": current_heading,
                    })
            except Exception as e:
                logger.warning(f"Error extracting PDF page {page_num}: {e}")
                pages.append({
                    "page_number": page_num,
                    "text": "",
                    "section_heading": current_heading,
                })
        return pages

    @staticmethod
    def _extract_docx(file_bytes: bytes) -> list[dict[str, Any]]:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        pages = []
        current_page = 1
        current_heading = "General"
        current_paras: list[str] = []

        for p in doc.paragraphs:
            text = clean_text(p.text)
            if not text:
                continue

            # Heading detection in docx
            style_name = (p.style.name or "").lower()
            if "heading" in style_name or text.isupper():
                if current_paras:
                    pages.append({
                        "page_number": current_page,
                        "text": "\n\n".join(current_paras),
                        "section_heading": current_heading,
                    })
                    current_paras = []
                    current_page += 1
                current_heading = text

            current_paras.append(text)

        if current_paras:
            pages.append({
                "page_number": current_page,
                "text": "\n\n".join(current_paras),
                "section_heading": current_heading,
            })

        return pages if pages else [{"page_number": 1, "text": "", "section_heading": "General"}]

    @staticmethod
    def _extract_txt(file_bytes: bytes) -> list[dict[str, Any]]:
        try:
            content = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content = file_bytes.decode("latin-1", errors="replace")

        cleaned = clean_text(content)
        heading = detect_section_heading(cleaned)
        return [{
            "page_number": 1,
            "text": cleaned,
            "section_heading": heading,
        }]

    @staticmethod
    def _extract_md(file_bytes: bytes) -> list[dict[str, Any]]:
        try:
            content = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content = file_bytes.decode("latin-1", errors="replace")

        cleaned = clean_text(content)
        # Split markdown by top-level headers (# Header)
        lines = cleaned.split("\n")
        sections = []
        current_heading = "Overview"
        current_lines: list[str] = []
        page_num = 1

        for line in lines:
            if line.startswith(("# ", "## ")):
                if current_lines:
                    sec_text = "\n".join(current_lines).strip()
                    if sec_text:
                        sections.append({
                            "page_number": page_num,
                            "text": sec_text,
                            "section_heading": current_heading,
                        })
                        page_num += 1
                        current_lines = []
                current_heading = line.lstrip("#").strip()
            current_lines.append(line)

        if current_lines:
            sec_text = "\n".join(current_lines).strip()
            if sec_text:
                sections.append({
                    "page_number": page_num,
                    "text": sec_text,
                    "section_heading": current_heading,
                })

        return sections if sections else [{"page_number": 1, "text": cleaned, "section_heading": "General"}]

    @staticmethod
    def _extract_csv(file_bytes: bytes) -> list[dict[str, Any]]:
        try:
            text_stream = io.StringIO(file_bytes.decode("utf-8"))
        except UnicodeDecodeError:
            text_stream = io.StringIO(file_bytes.decode("latin-1", errors="replace"))

        reader = csv.reader(text_stream)
        rows = list(reader)
        if not rows:
            return [{"page_number": 1, "text": "", "section_heading": "General"}]

        header = rows[0]
        header_line = " | ".join(header)
        data_rows = rows[1:]

        pages = []
        # Group CSV into pages of 20 rows each
        chunk_size = 20
        for i in range(0, max(1, len(data_rows)), chunk_size):
            batch = data_rows[i : i + chunk_size]
            formatted_lines = [header_line, "-" * len(header_line)]
            for r in batch:
                formatted_lines.append(" | ".join(r))
            page_text = "\n".join(formatted_lines)
            pages.append({
                "page_number": (i // chunk_size) + 1,
                "text": page_text,
                "section_heading": f"Data Rows {i+1} to {min(i + chunk_size, len(data_rows))}",
            })

        return pages


document_extractor = DocumentExtractor()
