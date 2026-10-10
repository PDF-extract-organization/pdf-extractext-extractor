from fastapi import FastAPI

from app.presentation.routers import extraction

app = FastAPI(title="pdf-extractext-extractor")
app.include_router(extraction.router)
