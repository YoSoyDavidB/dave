"""Document chunking utilities for RAG."""

import re
from dataclasses import dataclass
from collections.abc import Iterator


@dataclass
class DocumentChunk:
    """A chunk of a document for indexing."""

    content: str
    chunk_index: int
    start_char: int
    end_char: int
    metadata: dict


# Approximate tokens per character (conservative estimate)
CHARS_PER_TOKEN = 4
DEFAULT_CHUNK_SIZE = 500  # tokens
DEFAULT_CHUNK_OVERLAP = 50  # tokens


def estimate_tokens(text: str) -> int:
    """Estimate token count from text length.

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    return len(text) // CHARS_PER_TOKEN


def chunk_by_tokens(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> Iterator[DocumentChunk]:
    """Split text into chunks by approximate token count.

    Args:
        text: Text to chunk
        chunk_size: Target tokens per chunk
        chunk_overlap: Overlap tokens between chunks

    Yields:
        DocumentChunk objects
    """
    if not text.strip():
        return

    # Convert to character counts
    char_chunk_size = chunk_size * CHARS_PER_TOKEN
    char_overlap = chunk_overlap * CHARS_PER_TOKEN

    chunk_index = 0
    start = 0

    while start < len(text):
        # Calculate end position
        end = min(start + char_chunk_size, len(text))

        # Try to break at a sentence boundary if not at the end
        if end < len(text):
            # Look for sentence boundaries near the end
            search_start = max(start + char_chunk_size - 200, start)
            chunk_text = text[search_start:end + 100]

            # Find last sentence boundary
            boundaries = list(re.finditer(r'[.!?]\s+', chunk_text))
            if boundaries:
                # Use the last boundary found
                last_boundary = boundaries[-1]
                end = search_start + last_boundary.end()

        chunk_content = text[start:end].strip()

        if chunk_content:
            yield DocumentChunk(
                content=chunk_content,
                chunk_index=chunk_index,
                start_char=start,
                end_char=end,
                metadata={},
            )
            chunk_index += 1

        # Move start position with overlap
        start = end - char_overlap if end < len(text) else len(text)

        # Prevent infinite loop
        if start >= end:
            break


def chunk_markdown(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> Iterator[DocumentChunk]:
    """Split markdown text preserving structure where possible.

    Tries to split at:
    1. Heading boundaries (##, ###, etc.)
    2. Paragraph boundaries
    3. Sentence boundaries

    Args:
        text: Markdown text to chunk
        chunk_size: Target tokens per chunk
        chunk_overlap: Overlap tokens between chunks

    Yields:
        DocumentChunk objects with heading context
    """
    if not text.strip():
        return

    # Remove unused variable char_chunk_size
    # char_chunk_size = chunk_size * CHARS_PER_TOKEN

    # Split by headings first
    heading_pattern = r'^(#{1,6}\s+.+)$'
    sections = re.split(heading_pattern, text, flags=re.MULTILINE)

    current_heading = ""
    chunk_index = 0
    buffer = ""
    buffer_start = 0
    position = 0

    for section in sections:
        if not section.strip():
            position += len(section)
            continue

        # Check if this is a heading
        if re.match(r'^#{1,6}\s+', section):
            current_heading = section.strip()

            # If buffer is large enough, yield it
            if estimate_tokens(buffer) >= chunk_size // 2:
                if buffer.strip():
                    yield DocumentChunk(
                        content=buffer.strip(),
                        chunk_index=chunk_index,
                        start_char=buffer_start,
                        end_char=position,
                        metadata={"heading": current_heading},
                    )
                    chunk_index += 1
                buffer = ""
                buffer_start = position

            buffer += section + "\n"
            position += len(section)
            continue

        # Regular content - add to buffer
        section_tokens = estimate_tokens(section)

        if estimate_tokens(buffer) + section_tokens > chunk_size:
            # Buffer would be too large, yield current buffer
            if buffer.strip():
                yield DocumentChunk(
                    content=buffer.strip(),
                    chunk_index=chunk_index,
                    start_char=buffer_start,
                    end_char=position,
                    metadata={"heading": current_heading},
                )
                chunk_index += 1

            # If section itself is too large, chunk it further
            if section_tokens > chunk_size:
                for sub_chunk in chunk_by_tokens(section, chunk_size, chunk_overlap):
                    sub_chunk.chunk_index = chunk_index
                    sub_chunk.start_char += position
                    sub_chunk.end_char += position
                    sub_chunk.metadata["heading"] = current_heading
                    yield sub_chunk
                    chunk_index += 1
                buffer = ""
                buffer_start = position + len(section)
            else:
                # Start new buffer with heading context
                if current_heading:
                    buffer = current_heading + "\n\n" + section
                else:
                    buffer = section
                buffer_start = position
        else:
            buffer += section

        position += len(section)

    # Yield remaining buffer
    if buffer.strip():
        yield DocumentChunk(
            content=buffer.strip(),
            chunk_index=chunk_index,
            start_char=buffer_start,
            end_char=position,
            metadata={"heading": current_heading},
        )


def chunk_document(
    content: str,
    path: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[DocumentChunk]:
    """Chunk a document based on its type.

    Args:
        content: Document content
        path: File path (used to detect type)
        chunk_size: Target tokens per chunk
        chunk_overlap: Overlap between chunks

    Returns:
        List of DocumentChunk objects
    """
    # Use markdown chunking for .md files
    if path.endswith('.md'):
        chunks = list(chunk_markdown(content, chunk_size, chunk_overlap))
    else:
        chunks = list(chunk_by_tokens(content, chunk_size, chunk_overlap))

    # Add path to all chunk metadata
    for chunk in chunks:
        chunk.metadata["path"] = path

    return chunks
