import pytest
from app.ingestion.cleaner import clean_text, detect_section_heading
from app.ingestion.extractor import document_extractor
from app.ingestion.chunker import document_chunker
from app.ingestion.pipeline import validate_file, sanitize_filename
from app.embeddings import get_embedding_provider


def test_clean_text():
    dirty = "Hello   world!\r\n\r\n\r\n\nSection 1:\x00\x08Test"
    cleaned = clean_text(dirty)
    assert "Hello world!" in cleaned
    assert "\x00" not in cleaned
    assert "\x08" not in cleaned


def test_detect_section_heading():
    heading = detect_section_heading("# 1. Purpose and Scope\nThis SOP applies to...")
    assert heading == "1. Purpose and Scope"

    sop_heading = detect_section_heading("SOP-QA-042: Deviation Procedure\nStep 1...")
    assert "SOP-QA-042" in sop_heading


def test_validate_file_allowed_extensions():
    # Valid files
    is_valid, _, ext = validate_file("test.pdf", "application/pdf", 1024)
    assert is_valid is True
    assert ext == "pdf"

    is_valid, _, ext = validate_file("sop.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 2048)
    assert is_valid is True
    assert ext == "docx"

    is_valid, _, ext = validate_file("notes.txt", "text/plain", 512)
    assert is_valid is True
    assert ext == "txt"

    # Invalid extensions
    is_valid, err, _ = validate_file("malicious.exe", "application/octet-stream", 1024)
    assert is_valid is False
    assert "Unsupported file extension" in err

    # Empty file
    is_valid, err, _ = validate_file("empty.pdf", "application/pdf", 0)
    assert is_valid is False
    assert "empty" in err.lower()

    # Oversized file (>25MB)
    is_valid, err, _ = validate_file("huge.pdf", "application/pdf", 30 * 1024 * 1024)
    assert is_valid is False
    assert "exceeds maximum" in err.lower()


def test_sanitize_filename():
    unsafe = "../../../etc/passwd"
    assert ".." not in sanitize_filename(unsafe)
    assert "/" not in sanitize_filename(unsafe)
    assert "\\" not in sanitize_filename(unsafe)

    weird = "My SOP File (v1) [final]!.pdf"
    clean = sanitize_filename(weird)
    assert "My SOP File" in clean


def test_extract_txt():
    content = b"ACME PHARMA SOP\n\nSection 1: General Guidelines\nAll staff must comply."
    pages = document_extractor.extract(content, "txt")
    assert len(pages) == 1
    assert pages[0]["page_number"] == 1
    assert "ACME PHARMA" in pages[0]["text"]


def test_extract_md():
    content = b"# Header 1\nContent for section 1.\n\n## Header 2\nContent for section 2."
    pages = document_extractor.extract(content, "md")
    assert len(pages) >= 1
    assert any("Header" in p["section_heading"] for p in pages)


def test_chunker_preserves_metadata():
    pages = [
        {
            "page_number": 1,
            "section_heading": "Section 1",
            "text": "Paragraph 1 describing the deviation policy in full detail. " * 15,
        },
        {
            "page_number": 2,
            "section_heading": "Section 2",
            "text": "Paragraph 2 describing CAPA procedures and SLAs. " * 10,
        }
    ]
    chunks = document_chunker.chunk_document(pages)
    assert len(chunks) >= 2
    # Ensure page preservation
    page_numbers = {c["page_number"] for c in chunks}
    assert 1 in page_numbers
    assert 2 in page_numbers
    # Ensure chunk indexing is sequential
    for i, chunk in enumerate(chunks):
        assert chunk["chunk_index"] == i
        assert chunk["token_count"] > 0
        assert len(chunk["content"]) > 0


@pytest.mark.asyncio
async def test_embedding_provider():
    provider = get_embedding_provider()
    assert provider.dimension == 384

    texts = ["Acme Pharma SOP Deviation Management", "Temperature cold chain storage"]
    embeddings = await provider.embed_texts(texts)
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert len(embeddings[1]) == 384

    query_emb = await provider.embed_query("What is the CAPA timeline?")
    assert len(query_emb) == 384
