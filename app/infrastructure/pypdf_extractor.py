"""Adaptador del puerto PDFTextExtractor con pypdf."""

import io

from pypdf import PdfReader
from pypdf.errors import PyPdfError

from app.application.interfaces.pdf_extractor import (
    ExtractedPDF,
    InvalidPDFError,
    PDFTextExtractor,
)


class PyPDFTextExtractor(PDFTextExtractor):
    def extract_text(self, file_content: bytes, filename: str) -> ExtractedPDF:
        try:
            reader = PdfReader(io.BytesIO(file_content))
            pages = [page.extract_text() for page in reader.pages]
        except PyPdfError as error:
            raise InvalidPDFError(f"No se pudo leer el PDF: {error}") from error

        full_text = "\n\n".join(text for text in pages if text)

        return ExtractedPDF(
            filename=filename,
            text=full_text,
            page_count=len(pages),
            character_count=len(full_text),
        )
