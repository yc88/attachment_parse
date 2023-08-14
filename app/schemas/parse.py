import datetime

from pydantic import BaseModel, constr, Field
from typing import Any, Optional, Union


class ResponseModel(BaseModel):
    success: bool
    data: Any = None
    code: int
    message: str

    def get_dump(self):
        return self.model_dump()


class ParseRequest(BaseModel):
    """
    path 文件路径 本地文件路径和远程文件路径
    is_local 是否本地文件 默认 false path则是远程文件地址
    """
    path: constr(min_length=1)
    is_local: bool


class RegexField(BaseModel):
    phone_numbers: list = []  # 电话号码
    emails: list = []  # 邮箱
    addresses: list = []  # 地址
    company_names: list = []  # 公司名称
    countries: list = []  # 国家
    land_line: list = []  # 座机号码


class RegexFieldStatistical(BaseModel):
    phone_numbers: dict = {}  # 电话号码
    emails: dict = {}  # 邮箱
    addresses: dict = {}  # 地址
    company_names: dict = {}  # 公司名称
    countries: dict = {}  # 国家
    land_line: dict = {}  # 座机号码


class ExtraField(BaseModel):
    date: Any = None
    language: str = ""
    charset: str = ""
    subject: str = ""
    from_email: str = ""
    to_email: str = ""
    images: list = []
    link: list = []
    content_struct: str = ""


class FileParseResult(BaseModel):
    file_size: int  # 文件大小 b
    file_name: str  # 文件名称
    last_modified: str = ""  # 最后改变时间
    file_content: str  # 内容
    file_encoding: str = ""  # 编码格式
    regex_all: RegexField = None
    regex_all_statistical: RegexFieldStatistical = None
    extra: ExtraField = None
