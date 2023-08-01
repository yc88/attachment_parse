from fastapi import APIRouter, Depends
from app.schemas.parse import ParseRequest, ResponseModel
from app.services.attachment_parse import Service
from functools import lru_cache
from app.core.config import Settings
from typing import Annotated
import pytesseract

api = APIRouter(
    prefix="/attachment",
)


@lru_cache()
def get_settings():
    return Settings()


@api.post("/parser", response_model=ResponseModel)
async def parser(settings: Annotated[Settings, Depends(get_settings)], req: ParseRequest):
    result = await Service(settings).parser(req)
    return result
