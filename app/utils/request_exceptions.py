# !/usr/bin/env python
from fastapi.exceptions import RequestValidationError

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from app.schemas.parse import ResponseModel
from app.schemas.const import MyErrorCode, GetErrMsg


async def http_exception_handler(
        request: Request, exc: HTTPException
) -> JSONResponse:
    res = ResponseModel(success=False, data={}, code=MyErrorCode.InvalidArgument.value, message=exc.detail)
    return JSONResponse(res.get_dump(), status_code=exc.status_code)


async def request_validation_exception_handler(
        request: Request, exc: RequestValidationError
) -> JSONResponse:
    res = ResponseModel(success=False, data=exc.errors(), code=MyErrorCode.InvalidArgument.value,
                        message=GetErrMsg(MyErrorCode.InvalidArgument.value))
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content=res.get_dump(),
    )
