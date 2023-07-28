from fastapi import APIRouter, Depends
from app.schemas.parse import ParseRequest, ResponseModel
from app.services.attachment_parse import Service

api = APIRouter(
    prefix="/attachment",
)


@api.post("/parser", response_model=ResponseModel)
async def parser(req: ParseRequest):
    result = await Service().parser(req)
    return result
