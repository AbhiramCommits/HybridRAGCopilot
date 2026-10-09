from typing import List

from hybridrag.models import Chunk


def chunk_text(text: str, doc_id: str, metadata: dict, chunk_size: int = 320, overlap: int = 64) -> List[Chunk]:
    # Extract front matter if present
    front_matter = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            import yaml
            try:
                front_matter = yaml.safe_load(parts[1])
            except Exception:
                pass
            body = parts[2].strip()

    # Merge metadata
    meta = {**front_matter, **metadata}
    title = meta.get("title", "Untitled")
    category = meta.get("category", "general")
    department = meta.get("department", "General")
    effective_date = meta.get("effective_date", "2024-01-01")
    owner = meta.get("owner", "Admin")
    sensitivity = meta.get("sensitivity", "internal")

    # Split by headings or paragraphs first, then token-aware sliding window
    # We'll split body by headings (# or ##) to preserve heading path
    lines = body.split("\n")
    current_headings = []
    sections = []
    current_section_lines = []

    for line in lines:
        if line.startswith("#"):
            if current_section_lines:
                sections.append((current_headings.copy(), "\n".join(current_section_lines)))
                current_section_lines = []
            header_text = line.lstrip("#").strip()
            # update headings hierarchy
            hash_count = len(line) - len(line.lstrip("#"))
            if hash_count <= len(current_headings):
                current_headings = current_headings[:hash_count-1]
            current_headings.append(header_text)
        else:
            current_section_lines.append(line)
    if current_section_lines:
        sections.append((current_headings.copy(), "\n".join(current_section_lines)))

    chunks = []
    chunk_counter = 0

    for heading_path, sec_text in sections:
        # Split sec_text into sentences or words for chunking
        words = sec_text.split()
        if not words:
            continue

        # Sliding window over words
        i = 0
        while i < len(words):
            window_words = words[i:i + chunk_size]
            chunk_content = " ".join(window_words)

            chunk_id = f"{doc_id}-CHK-{chunk_counter:03d}"
            chunks.append(Chunk(
                chunk_id=chunk_id,
                doc_id=doc_id,
                title=title,
                category=category,
                department=department,
                effective_date=effective_date,
                owner=owner,
                sensitivity=sensitivity,
                heading_path=heading_path,
                content=chunk_content,
                source_type="unstructured"
            ))
            chunk_counter += 1
            if i + chunk_size >= len(words):
                break
            i += (chunk_size - overlap)

    # Fallback if no sections or chunks produced
    if not chunks:
        chunks.append(Chunk(
            chunk_id=f"{doc_id}-CHK-000",
            doc_id=doc_id,
            title=title,
            category=category,
            department=department,
            effective_date=effective_date,
            owner=owner,
            sensitivity=sensitivity,
            heading_path=[],
            content=body,
            source_type="unstructured"
        ))

    return chunks
