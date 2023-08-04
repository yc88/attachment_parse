from fastapi import APIRouter, Depends
from app.schemas.parse import ParseRequest, ResponseModel
from app.services.attachment_parse import Service
from app.services.base import Base
from functools import lru_cache
from app.core.config import Settings
from typing import Annotated
import pytesseract

attachmentApi = APIRouter(
    prefix="/attachment",
)

baseApi = APIRouter(
    prefix="/base",
)


@lru_cache()
def get_settings():
    return Settings()


@attachmentApi.post("/parser", response_model=ResponseModel)
async def parser(settings: Annotated[Settings, Depends(get_settings)], req: ParseRequest):
    result = await Service(settings).parser(req)
    return result


@baseApi.get("/language")
async def language(settings: Annotated[Settings, Depends(get_settings)]):
    result = await Base(settings).language()
    return result
