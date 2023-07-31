import csv
import json
import os
import datetime
import requests

from app.schemas.const import MyErrorCode, HttpStatusCode
from app.schemas.parse import FileParseResult, RegexField, RegexFieldStatistical, ExtraField
from app.utils.app_exceptions import UnicornException
from app.api.content_regex import get_regex_val
import chardet


def parse_local_csv_file(file_path):
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

        with open(file_path, 'r', encoding=encoding) as file:
            csv_reader = csv.reader(file)
            titles = next(csv_reader)  # 获取标题行
            contents = list(csv_reader)

        return get_return_result(contents, titles, "", file_size, file_name, last_modified, encoding)
    except Exception as e:
        raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                               MyErrorCode.InvalidArgument.value,
                               e.__str__())


def parse_remote_csv_file(file_url):
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
            # 获取最后修改时间
            last_modified = response.headers.get("Last-Modified")
            if not last_modified:
                last_modified = ""
            if last_modified is not str:
                last_modified = str(last_modified)
            # 获取编码格式
            file_encoding = chardet.detect(response.content)['encoding']

            # 使用 StringIO 创建一个类文件对象
            from io import StringIO
            csv_file = StringIO(response.text)
            # 解析 CSV 文件
            reader = csv.reader(csv_file)
            data = [row for row in reader]
            # 获取标题行
            titles = data[0]
            # 获取内容行
            content = data[1:]
            return get_return_result(content, titles, file_encoding, file_size, file_name, last_modified,
                                     encoding)
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
    title = '\n'.join(titles)
    # 获取 body 内容
    file_content = '\n'.join([vv for c in contents for vv in c if vv])
    result = [{header: [value[i] for value in contents]} for i, header in enumerate(titles)]

    regex_all, regex_all_statistical = get_regex_val(file_content)
    if not file_encoding:
        file_encoding = ""
    extra_field = ExtraField(
        date="",
        language="",
        charset=file_encoding,
        subject=title,
        images=[],
        link=[],
        content_struct=str(result)
    )
    return FileParseResult(file_size=file_size, file_name=file_name, last_modified=last_modified,
                           file_content=file_content, file_encoding=encoding,
                           regex_all=regex_all, regex_all_statistical=regex_all_statistical, extra=extra_field)
