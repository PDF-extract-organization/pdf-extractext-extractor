# pdf-extractext-extractor

Microservicio que extrae el texto de un PDF. Forma parte de
[pdf-extractext](https://github.com/PDF-extract-organization/pdf-extractext), dividido
en microservicios (épica: pdf-extractext#64).

Recibe bytes y devuelve texto. No habla con la IA, ni con la base de datos, ni guarda
archivos: el PDF se procesa en memoria y se descarta.

## Contrato HTTP

El servicio escucha en el puerto `8000` y no sabe nada de Traefik. En el stack
completo, Traefik le quita el prefijo `/extractor` antes de reenviar, así que desde
fuera las rutas son `http://pdf.localhost/extractor/...`.

| Método y ruta | Entrada | Respuesta |
|---|---|---|
| `POST /extract` | `multipart/form-data` con el campo `file` (PDF) | `200` `{"filename", "text", "page_count", "character_count"}` |
| `GET /health` | — | `200` `{"status": "healthy", "service": "extractor"}` |

Las páginas se unen con una línea en blanco (`\n\n`).

### Errores

Todos devuelven `{"detail": "..."}` en español.

| Código | Cuándo |
|---|---|
| `400` | El archivo no es un PDF válido, está dañado o vacío |
| `413` | Supera `MAX_FILE_SIZE_MB`. Se comprueba sin leer más allá del límite |
| `422` | Falta el campo `file`, o el PDF no tiene texto extraíble (menos de 10 caracteres; probablemente escaneado). El OCR queda fuera de alcance (#4) |

## Configuración

| Variable | Por defecto | Uso |
|---|---|---|
| `MAX_FILE_SIZE_MB` | `10` | Tamaño máximo del PDF |

Ver `.env.example`.

## Desarrollo

```bash
uv sync --group dev
uv run pytest                      # tests sin red ni servicios externos
uv run uvicorn app.main:app --reload
```

## Docker

```bash
docker build -t pdf-extractext-extractor .
docker run -p 8000:8000 pdf-extractext-extractor

curl -F "file=@documento.pdf" http://localhost:8000/extract
curl http://localhost:8000/health
```

La imagen corre con un usuario sin privilegios y declara un `HEALTHCHECK` sobre
`/health`. Al integrar en `main`, la CI la publica en
`ghcr.io/pdf-extract-organization/pdf-extractext-extractor`.

## Arquitectura

| Capa | Contiene |
|---|---|
| `app/application/interfaces` | Puerto `PDFTextExtractor`, `ExtractedPDF`, `InvalidPDFError` |
| `app/application/services` | `ExtractionService`: exige un mínimo de texto |
| `app/infrastructure` | `PyPDFTextExtractor`: el único sitio que importa `pypdf` |
| `app/presentation` | Router y schemas de FastAPI |
| `app/dependencies.py` | Cableado; lo importan el router y `main`, sin ciclos |

## Flujo de trabajo

`main` y `develop` son las ramas principales. Los cambios entran por pull request a
`develop`, con los tests en verde en la CI. Los commits citan el issue (`#1`).
