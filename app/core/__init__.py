"""Configuración leída de variables de entorno o del .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    max_file_size_mb: int = 10

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
