import json
import os
import datetime
import requests

from app.schemas.const import MyErrorCode, HttpStatusCode
from app.schemas.parse import FileParseResult, RegexField, RegexFieldStatistical, ExtraField
from app.utils.app_exceptions import UnicornException
from app.api.content_regex import get_regex_val
from bs4 import BeautifulSoup
from collections import OrderedDict
import pandas
import chardet
from io import BytesIO


def parse_local_xls_file(file_path):
    """
    解析本地的 .xls .xlsx文件内容
    """
    try:
        # 获取文件内容和编码方式
        encoding = 'utf-8'
        # 获取文件名称
        file_name = os.path.basename(file_path)
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        # 获取最后修改时间
        last_modified = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')

        xls_data = pandas.read_excel(file_path)
        # 获取表格标题
        titles = list(xls_data.columns)
        # 获取表格内容
        content = xls_data.to_dict(orient='records')
        with open(file_path, 'rb') as file:
            file_content = file.read()
            file_encoding = chardet.detect(file_content)['encoding']

        return get_return_result(content, titles, file_encoding, file_size, file_name, last_modified, encoding)
    except Exception as e:
        raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                               MyErrorCode.InvalidArgument.value,
                               e.__str__())


def parse_remote_xls_file(file_url):
    try:
        # 获取文件内容和编码方式
        encoding = 'utf-8'
        # 下载远程文件内容
        response = requests.get(file_url)
        if response.status_code == 200:
            # 获取文件名称
            file_name = os.path.basename(file_url)
            # 文件内容
            raw_content = response.text
            # 获取文件大小
            file_size = len(raw_content)

            # 将文件内容读取为BytesIO对象
            xls_data = BytesIO(response.content)
            # 解析XLS文件内容
            xls_df = pandas.read_excel(xls_data, sheet_name=0)  # 假设你要解析的是第一个工作表，如果有多个工作表需要调整sheet_name参数
            # 获取最后修改时间
            last_modified = response.headers.get("Last-Modified")
            if not last_modified:
                last_modified = ""
            if last_modified is not str:
                last_modified = str(last_modified)
            # 获取编码格式
            file_encoding = chardet.detect(response.content)['encoding']
            # 获取表格标题
            titles = list(xls_df.columns)
            # 获取表格内容
            content = xls_df.to_dict(orient='records')
            return get_return_result(content, titles, file_encoding, file_size, file_name, last_modified,
                                     encoding=encoding)
        else:
            raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                                   MyErrorCode.InvalidArgument.value,
                                   " 请求错误 ")
    except Exception as e:
        raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                               MyErrorCode.InvalidArgument.value,
                               e.__str__())


def get_return_result(contents, titles, file_encoding, file_size, file_name, last_modified, encoding):
    # 获取标题
    title = str(titles)
    # 获取 body 内容
    file_content = ""
    for c in contents:
        for v in c:
            val = c[v]
            v_str = str(val)
            if v_str == 'nan':
                continue
            if v_str:
                file_content += " \n " + v_str
    # 语言
    # Get encoding format
    charset = file_encoding
    if not charset:
        charset = ""
    if charset is not str:
        charset = str(charset)

    regex_all, regex_all_statistical = get_regex_val(file_content)

    extra_field = ExtraField(
        date="",
        language="",
        charset=charset,
        subject=title,
        images=[],
        link=[],
        content_struct=str(contents)
    )
    return FileParseResult(file_size=file_size, file_name=file_name, last_modified=last_modified,
                           file_content=file_content, file_encoding=encoding,
                           regex_all=regex_all, regex_all_statistical=regex_all_statistical, extra=extra_field)
