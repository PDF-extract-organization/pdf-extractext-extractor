"""Cableado de dependencias. Router y main lo importan; él no importa a ninguno."""

from functools import lru_cache

from app.application.services.extraction_service import ExtractionService
from app.core import Settings
from app.infrastructure.pypdf_extractor import PyPDFTextExtractor


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_extraction_service() -> ExtractionService:
    return ExtractionService(PyPDFTextExtractor())
