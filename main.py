#!/usr/bin/env python
import uvicorn

from app.utils.app_exceptions import UnicornException
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.utils.request_exceptions import (
    http_exception_handler,
    request_validation_exception_handler,
)
from app.utils.app_exceptions import app_exception_handler

from app.routers.api import attachmentApi, baseApi

app = FastAPI()


#
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, e):
    return await http_exception_handler(request, e)


#
@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request, e):
    return await request_validation_exception_handler(request, e)


# 自定义返回
@app.exception_handler(UnicornException)
async def custom_app_exception_handler(request, e):
    return await app_exception_handler(request, e)


app.include_router(attachmentApi, prefix="")
app.include_router(baseApi)


@app.get("/")
async def root():
    return {"message": "successful"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, log_level="debug", reload=True)
