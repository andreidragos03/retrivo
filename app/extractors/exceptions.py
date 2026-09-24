class DocumentExtractionError(Exception):
    """Raised when text cannot be extracted from a document."""

class NoExtractableTextError(DocumentExtractionError):
    """Raised when a document is valid but contains no extractable text."""
