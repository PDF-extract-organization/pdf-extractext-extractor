"""Tests del caso de uso, con un doble del extractor (sin pypdf)."""

import pytest

from app.application.interfaces.pdf_extractor import ExtractedPDF, PDFTextExtractor
from app.application.services.extraction_service import (
    ExtractionService,
    NoExtractableTextError,
)


class FakeExtractor(PDFTextExtractor):
    def __init__(self, text: str):
        self._text = text
        self.received: tuple[bytes, str] | None = None

    def extract_text(self, file_content: bytes, filename: str) -> ExtractedPDF:
        self.received = (file_content, filename)
        return ExtractedPDF(
            filename=filename,
            text=self._text,
            page_count=1,
            character_count=len(self._text),
        )


def test_devuelve_lo_que_extrae_el_extractor():
    service = ExtractionService(FakeExtractor("Un texto suficientemente largo"))

    result = service.extract(b"bytes", "doc.pdf")

    assert result.text == "Un texto suficientemente largo"


def test_pasa_el_contenido_y_el_nombre_al_extractor():
    extractor = FakeExtractor("Un texto suficientemente largo")

    ExtractionService(extractor).extract(b"bytes", "doc.pdf")

    assert extractor.received == (b"bytes", "doc.pdf")


@pytest.mark.parametrize("texto", ["", "   \n\t ", "a" * 9])
def test_rechaza_un_texto_vacio_o_demasiado_corto(texto):
    service = ExtractionService(FakeExtractor(texto))

    with pytest.raises(NoExtractableTextError):
        service.extract(b"bytes", "escaneado.pdf")


def test_acepta_un_texto_de_exactamente_10_caracteres():
    service = ExtractionService(FakeExtractor("a" * 10))

    assert service.extract(b"bytes", "doc.pdf").text == "a" * 10
