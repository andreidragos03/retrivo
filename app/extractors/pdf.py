import pymupdf

from app.extractors.exceptions import DocumentExtractionError, NoExtractableTextError

def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        document = pymupdf.open(
            stream = file_bytes,
            filetype = "pdf"
        )
    except Exception as exc:
        raise DocumentExtractionError(
            "Unable to open PDF document."
        ) from exc

    try:
        pages = []

        for page in document:
            text = page.get_text()
            pages.append(text)

        extracted_text = "\n".join(pages)

        if not extracted_text.strip():
            raise NoExtractableTextError(
                "The PDF contains no extractable text."
            )

        return extracted_text
    except NoExtractableTextError:
        raise
    except Exception as exc:
        raise DocumentExtractionError(
            "Unable to extract text from PDF document."
        ) from exc
    finally:
        document.close()
