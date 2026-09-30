def _split_text(
    text: str,
    chunk_size: int,
    separators: list[str]
) -> list[str]:
    if len(text) <= chunk_size:
        return [text]

    if not separators:
        return [
            text[i : i + chunk_size]
            for i in range(0, len(text), chunk_size)
        ]

    separator = separators[0]
    remaining_separators = separators[1:]

    if separator == "":
        return _split_text(
            text = text,
            chunk_size = chunk_size,
            separators = [],
        )

    if separator not in text:
        return _split_text(
            text = text,
            chunk_size = chunk_size,
            separators = remaining_separators
        )

    raw_parts = text.split(separator)

    parts = []

    for index, part in enumerate(raw_parts):
        if index < len(raw_parts) - 1:
            part += separator

        if part:
            parts.append(part)

    result = []

    for part in parts:
        if len(part) <= chunk_size:
            result.append(part)
        else:
            result.extend(
                _split_text(
                    text = part,
                    chunk_size = chunk_size,
                    separators = remaining_separators
                )
            )

    return result


def _merge_chunks(
    pieces: list[str],
    chunk_size: int,
    chunk_overlap: int
) -> list[str]:
    if not pieces:
        return []

    chunks = []
    current_pieces = []
    current_length = 0

    for piece in pieces:
        piece_length = len(piece)

        if current_pieces and current_length + piece_length > chunk_size:
            chunks.append("".join(current_pieces))

            if chunk_overlap == 0:
                current_pieces = []
                current_length = 0
            else:
                while current_pieces and (
                    current_length - len(current_pieces[0]) >= chunk_overlap
                    or current_length + piece_length > chunk_size
                ):
                    removed_piece = current_pieces.pop(0)
                    current_length -= len(removed_piece)

        current_pieces.append(piece)
        current_length += piece_length

    if current_pieces:
        chunks.append("".join(current_pieces))

    return chunks


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    if not text.strip():
        return []

    pieces = _split_text(
        text = text,
        chunk_size = chunk_size,
        separators = ["\n\n", "\n", " ", ""]
    )

    return _merge_chunks(
        pieces = pieces,
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap
    )
