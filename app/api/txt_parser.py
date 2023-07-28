import os
import time

import requests

from app.schemas.const import MyErrorCode, HttpStatusCode
from app.schemas.parse import FileParseResult
from app.utils.app_exceptions import UnicornException
from app.api.content_regex import get_regex_val


def parse_local_text_file(file_path):
    """
    解析本地的txt文件内容
    """
    try:

        # 获取文件内容和编码方式
        encoding = 'utf-8'
        # 获取文件名称
        file_name = os.path.basename(file_path)
        # 获取文件大小
        file_size = os.path.getsize(file_path)

        with open(file_path, 'r', encoding=encoding) as file:
            file_content = file.read()

        regex_all, regex_all_statistical = get_regex_val(file_content)

        # 获取文件更改时间
        file_change_times = os.path.getmtime(file_path)
        file_change_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_change_times))
        return FileParseResult(file_size=file_size, file_name=file_name, file_change_time=file_change_time,
                               file_content=file_content, file_encoding=encoding,
                               regex_all=regex_all, regex_all_statistical=regex_all_statistical)
    except Exception as e:
        raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                               MyErrorCode.InvalidArgument.value,
                               e.__str__())


def parse_remote_text_file(file_url):
    try:
        # 下载远程文件内容
        response = requests.get(file_url)
        if response.status_code == 200:
            # 获取文件名称
            file_name = os.path.basename(file_url)
            # 文件内容
            raw_content = response.content
            # 获取文件大小
            file_size = len(raw_content)
            # file_content = response.text
            encoding = 'utf-8'
            file_content = raw_content.decode(encoding, errors='ignore')

            regex_all, regex_all_statistical = get_regex_val(file_content)

            return FileParseResult(file_size=file_size, file_name=file_name, file_content=file_content,
                                   file_encoding=encoding,
                                   regex_all=regex_all, regex_all_statistical=regex_all_statistical)
        else:
            raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                                   MyErrorCode.InvalidArgument.value,
                                   " 请求错误 ")
    except Exception as e:
        raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                               MyErrorCode.InvalidArgument.value,
                               e.__str__())
