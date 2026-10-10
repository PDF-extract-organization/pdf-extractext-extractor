"""Puerto de extracción de texto: el núcleo no conoce ninguna librería de PDF."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


class InvalidPDFError(Exception):
    """El contenido no es un PDF legible (corrupto, vacío o no es un PDF)."""


@dataclass
class ExtractedPDF:
    filename: str
    text: str
    page_count: int
    character_count: int


class PDFTextExtractor(ABC):
    @abstractmethod
    def extract_text(self, file_content: bytes, filename: str) -> ExtractedPDF:
        """Extrae el texto del PDF. Lanza InvalidPDFError si no se puede leer."""
