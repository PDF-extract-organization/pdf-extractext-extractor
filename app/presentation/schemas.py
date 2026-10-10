from pydantic import BaseModel


class ExtractResponse(BaseModel):
    filename: str
    text: str
    page_count: int
    character_count: int


class HealthResponse(BaseModel):
    status: str
    service: str
