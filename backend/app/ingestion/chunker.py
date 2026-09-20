import logging
from typing import Any

logger = logging.getLogger(__name__)


class DocumentChunker:
    """Chunks extracted pages/sections into overlapping segments preserving page and heading metadata."""

    def __init__(self, target_chunk_chars: int = 700, overlap_chars: int = 100):
        self.target_chunk_chars = target_chunk_chars
        self.overlap_chars = overlap_chars

    def chunk_document(self, pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Splits document pages into chunks with full source citation metadata."""
        chunks: list[dict[str, Any]] = []
        global_chunk_idx = 0

        for page in pages:
            page_num = page.get("page_number", 1)
            heading = page.get("section_heading", "General")
            text = page.get("text", "").strip()

            if not text:
                continue

            # If the page text is small enough, it becomes a single chunk
            if len(text) <= self.target_chunk_chars:
                token_count = max(1, len(text) // 4)
                chunks.append({
                    "chunk_index": global_chunk_idx,
                    "content": text,
                    "page_number": page_num,
                    "section_heading": heading,
                    "token_count": token_count,
                })
                global_chunk_idx += 1
                continue

            # Otherwise, split by paragraphs first
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            current_buffer = ""

            for para in paragraphs:
                if len(current_buffer) + len(para) + 2 <= self.target_chunk_chars:
                    if current_buffer:
                        current_buffer += "\n\n" + para
                    else:
                        current_buffer = para
                else:
                    if current_buffer:
                        token_count = max(1, len(current_buffer) // 4)
                        chunks.append({
                            "chunk_index": global_chunk_idx,
                            "content": current_buffer,
                            "page_number": page_num,
                            "section_heading": heading,
                            "token_count": token_count,
                        })
                        global_chunk_idx += 1

                        # Take overlap from the end of current_buffer
                        overlap = current_buffer[-self.overlap_chars :] if len(current_buffer) > self.overlap_chars else ""
                        if overlap:
                            current_buffer = overlap + " " + para
                        else:
                            current_buffer = para
                    else:
                        # Paragraph itself exceeds target_chunk_chars: hard-slice by sentences / words
                        start = 0
                        while start < len(para):
                            end = min(start + self.target_chunk_chars, len(para))
                            sub_chunk = para[start:end].strip()
                            if sub_chunk:
                                chunks.append({
                                    "chunk_index": global_chunk_idx,
                                    "content": sub_chunk,
                                    "page_number": page_num,
                                    "section_heading": heading,
                                    "token_count": max(1, len(sub_chunk) // 4),
                                })
                                global_chunk_idx += 1
                            start += self.target_chunk_chars - self.overlap_chars
                        current_buffer = ""

            if current_buffer.strip():
                chunks.append({
                    "chunk_index": global_chunk_idx,
                    "content": current_buffer.strip(),
                    "page_number": page_num,
                    "section_heading": heading,
                    "token_count": max(1, len(current_buffer) // 4),
                })
                global_chunk_idx += 1

        return chunks


document_chunker = DocumentChunker()
