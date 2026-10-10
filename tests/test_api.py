"""Tests de los endpoints HTTP. No hay red ni servicios externos."""

import pytest
from fastapi.testclient import TestClient

from app.core import Settings
from app.dependencies import get_settings
from app.main import app
from tests.conftest import build_pdf


@pytest.fixture
def client():
    yield TestClient(app)
    app.dependency_overrides.clear()


def subir(client, contenido: bytes, filename: str = "doc.pdf"):
    return client.post(
        "/extract", files={"file": (filename, contenido, "application/pdf")}
    )


def test_extract_devuelve_texto_paginas_y_caracteres(client, pdf_bytes):
    response = subir(client, pdf_bytes)

    assert response.status_code == 200
    assert response.json() == {
        "filename": "doc.pdf",
        "text": "Hola mundo desde un PDF de prueba",
        "page_count": 1,
        "character_count": 33,
    }


def test_extract_une_varias_paginas(client, multipage_pdf_bytes):
    body = subir(client, multipage_pdf_bytes).json()

    assert body["text"] == "Primera pagina\n\nSegunda pagina"
    assert body["page_count"] == 2


def test_extract_sin_archivo_devuelve_422(client):
    assert client.post("/extract").status_code == 422


def test_extract_con_un_pdf_corrupto_devuelve_400(client):
    response = subir(client, b"esto no es un pdf")

    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


def test_extract_con_un_archivo_vacio_devuelve_400(client):
    assert subir(client, b"").status_code == 400


def test_extract_con_un_pdf_sin_texto_devuelve_422(client):
    response = subir(client, build_pdf([""]))

    assert response.status_code == 422
    assert "escaneado" in response.json()["detail"]


def test_extract_rechaza_un_archivo_mayor_que_el_limite_con_413(client, pdf_bytes):
    app.dependency_overrides[get_settings] = lambda: Settings(max_file_size_mb=0)

    response = subir(client, pdf_bytes)

    assert response.status_code == 413
    assert "0MB" in response.json()["detail"]


def test_extract_acepta_un_archivo_dentro_del_limite(client, pdf_bytes):
    app.dependency_overrides[get_settings] = lambda: Settings(max_file_size_mb=1)

    assert subir(client, pdf_bytes).status_code == 200


def test_health_responde_healthy(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "extractor"}
