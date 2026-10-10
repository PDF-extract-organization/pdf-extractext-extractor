"""Tests del adaptador de pypdf, con PDFs reales construidos a mano."""

import pytest

from app.application.interfaces.pdf_extractor import InvalidPDFError
from app.infrastructure.pypdf_extractor import PyPDFTextExtractor
from tests.conftest import build_pdf


@pytest.fixture
def extractor() -> PyPDFTextExtractor:
    return PyPDFTextExtractor()


def test_extrae_el_texto_de_un_pdf_de_una_pagina(extractor, pdf_bytes):
    result = extractor.extract_text(pdf_bytes, "doc.pdf")

    assert result.text == "Hola mundo desde un PDF de prueba"


def test_devuelve_el_nombre_del_archivo(extractor, pdf_bytes):
    assert extractor.extract_text(pdf_bytes, "doc.pdf").filename == "doc.pdf"


def test_une_las_paginas_con_una_linea_en_blanco(extractor, multipage_pdf_bytes):
    result = extractor.extract_text(multipage_pdf_bytes, "doc.pdf")

    assert result.text == "Primera pagina\n\nSegunda pagina"


def test_cuenta_las_paginas(extractor, multipage_pdf_bytes):
    assert extractor.extract_text(multipage_pdf_bytes, "doc.pdf").page_count == 2


def test_cuenta_los_caracteres_con_un_valor_literal(extractor):
    result = extractor.extract_text(build_pdf(["abcde"]), "doc.pdf")

    assert result.character_count == 5


def test_un_pdf_sin_texto_devuelve_texto_vacio(extractor):
    result = extractor.extract_text(build_pdf([""]), "vacio.pdf")

    assert result.text == ""
    assert result.character_count == 0
    assert result.page_count == 1


def test_bytes_que_no_son_un_pdf_lanzan_invalid_pdf_error(extractor):
    with pytest.raises(InvalidPDFError):
        extractor.extract_text(b"esto no es un pdf", "falso.pdf")


def test_un_archivo_vacio_lanza_invalid_pdf_error(extractor):
    with pytest.raises(InvalidPDFError):
        extractor.extract_text(b"", "vacio.pdf")


def test_un_pdf_truncado_lanza_invalid_pdf_error(extractor, pdf_bytes):
    with pytest.raises(InvalidPDFError):
        extractor.extract_text(pdf_bytes[: len(pdf_bytes) // 2], "roto.pdf")
