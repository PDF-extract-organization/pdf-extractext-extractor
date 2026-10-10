from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from app.application.interfaces.pdf_extractor import InvalidPDFError
from app.application.services.extraction_service import (
    ExtractionService,
    NoExtractableTextError,
)
from app.core import Settings
from app.dependencies import get_extraction_service, get_settings
from app.presentation.schemas import ExtractResponse, HealthResponse

router = APIRouter()


@router.post("/extract", response_model=ExtractResponse)
async def extract(
    file: UploadFile = File(...),
    service: ExtractionService = Depends(get_extraction_service),
    settings: Settings = Depends(get_settings),
):
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    content = await file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"El archivo es demasiado grande. El límite es de {settings.max_file_size_mb}MB.",
        )

    try:
        return await run_in_threadpool(service.extract, content, file.filename)
    except InvalidPDFError:
        raise HTTPException(
            status_code=400, detail="El archivo no es un PDF válido o está dañado."
        )
    except NoExtractableTextError:
        raise HTTPException(
            status_code=422,
            detail="El PDF no contiene texto extraíble. Es probable que sea un documento escaneado o una imagen.",
        )


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy", service="extractor")
