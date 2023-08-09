# !/usr/bin/env python

import sys
import traceback
from fastapi import Request
from starlette.responses import JSONResponse
from app.schemas.parse import ResponseModel
from typing import Any, Union
from app.schemas.const import GetErrMsg


class UnicornException(Exception):
    def __init__(self, status_code: int, code: int, message: str, data: Union[Any, None] = None):
        self.exception_case = self.__class__.__name__
        self.status_code = status_code
        self.code = code
        self.message = message
        self.data = data
        super().__init__(status_code, code, message, data)


async def app_exception_handler(request: Request, exc: UnicornException):
    msg = exc.message
    if msg == "":
        msg = GetErrMsg(exc.code)
    res = ResponseModel(success=False, data=exc.data, code=exc.code,
                        message=msg)
    exc_info = sys.exc_info()  # Get exception information
    exc_type, exc_value, exc_traceback = exc_info
    error_message = "".join(traceback.format_tb(exc_traceback))
    print(error_message)
    return JSONResponse(
        status_code=exc.status_code,
        content=res.get_dump(),
    )
