import pytest

from app.chunking.text import chunk_text


def test_text_smaller_than_chunk_size_returns_single_chunk():
    text = "Retrivo is an AI knowledge retrieval platform."

    chunks = chunk_text(
        text = text,
        chunk_size = 100,
        chunk_overlap = 20
    )

    assert chunks == [text]

def test_text_is_split_when_larger_than_chunk_size():
    text = "abcdefghij"

    chunks = chunk_text(
        text = text,
        chunk_size = 4,
        chunk_overlap = 0
    )

    assert chunks == [
        "abcd",
        "efgh",
        "ij"
    ]

def test_chunks_preserve_overlap():
    text = "aaaa bbbb cccc dddd"

    chunks = chunk_text(
        text = text,
        chunk_size = 10,
        chunk_overlap = 5,
    )

    assert chunks == [
        "aaaa bbbb ",
        "bbbb cccc ",
        "cccc dddd",
    ]

def test_overlap_can_exceed_target_to_preserve_natural_boundary():
    text = "aaaaaa bbbbbb cccccc"

    chunks = chunk_text(
        text = text,
        chunk_size = 14,
        chunk_overlap = 5,
    )

    assert chunks == [
        "aaaaaa bbbbbb ",
        "bbbbbb cccccc",
    ]

def test_overlap_is_reduced_when_needed_to_respect_chunk_size():
    text = "aaaaaa bbbbbb ccccccccc"

    chunks = chunk_text(
        text = text,
        chunk_size = 10,
        chunk_overlap = 5,
    )

    assert chunks == [
        "aaaaaa ",
        "bbbbbb ",
        "ccccccccc",
    ]

def test_empty_text_returns_no_chunks():
    assert chunk_text("", chunk_size = 100, chunk_overlap = 20) == []
    assert chunk_text("   \n\n   ", chunk_size = 100, chunk_overlap = 20) == []


def test_chunk_size_must_be_positive():
    with pytest.raises(ValueError, match = "chunk_size must be greater than 0"):
        chunk_text("hello", chunk_size = 0, chunk_overlap = 0)


def test_chunk_overlap_cannot_be_negative():
    with pytest.raises(ValueError, match = "chunk_overlap cannot be negative"):
        chunk_text("hello", chunk_size = 10, chunk_overlap = -1)


def test_chunk_overlap_must_be_smaller_than_chunk_size():
    with pytest.raises(ValueError, match = "chunk_overlap must be smaller than chunk_size"):
        chunk_text("hello", chunk_size = 10, chunk_overlap = 10)
