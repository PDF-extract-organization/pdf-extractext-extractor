"""Caso de uso: extraer el texto de un PDF y asegurar que hay algo que resumir."""

from app.application.interfaces.pdf_extractor import ExtractedPDF, PDFTextExtractor

MIN_EXTRACTED_CHARS = 10


class NoExtractableTextError(Exception):
    """El PDF es válido pero no tiene texto (probablemente un escaneo)."""


class ExtractionService:
    def __init__(self, extractor: PDFTextExtractor):
        self._extractor = extractor

    def extract(self, file_content: bytes, filename: str) -> ExtractedPDF:
        extracted = self._extractor.extract_text(file_content, filename)

        if len(extracted.text.strip()) < MIN_EXTRACTED_CHARS:
            raise NoExtractableTextError("El PDF no contiene texto extraíble suficiente.")

        return extracted
