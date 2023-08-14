import os
import io

import requests

from app.schemas.const import MyErrorCode, HttpStatusCode
from app.schemas.parse import FileParseResult
from app.utils.app_exceptions import UnicornException
from app.api.content_regex import RegexRules, get_regex_val
from app.schemas.parse import RegexField, RegexFieldStatistical, ExtraField
from datetime import datetime, timezone, timedelta
import PyPDF2


def parse_local_pdf_file(file_path):
    """
    解析本地的pdf文件内容
    """
    try:
        encoding = 'utf-8'
        # 获取文件名称
        file_name = os.path.basename(file_path)
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        # 获取最后修改时间
        last_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        # 获取文件内容和编码方式
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfFileReader(file)
            num_pages = pdf_reader.numPages
            metadata = pdf_reader.getDocumentInfo()
            text = ""
            for page_num in range(num_pages):
                page = pdf_reader.getPage(page_num)
                text += page.extractText()
        return get_return_result(text, metadata, encoding, file_name, file_size, last_modified)
    except Exception as e:
        raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                               MyErrorCode.InvalidArgument.value,
                               e.__str__())


def parse_remote_pdf_file(file_url):
    try:
        encoding = 'utf-8'
        # 下载远程文件内容
        response = requests.get(file_url)
        if response.status_code == 200:
            # 获取文件名称
            file_name = os.path.basename(file_url)
            # 文件内容
            raw_content = response.content
            # 获取文件大小
            file_size = len(raw_content)


            # 获取最后修改时间
            last_modified = response.headers.get('Last-Modified')
            if last_modified:
                last_modified_datetime = datetime.strptime(last_modified,
                                                           '%a, %d %b %Y %H:%M:%S %Z').replace(tzinfo=timezone.utc)
                cst_time = last_modified_datetime.astimezone(timezone(timedelta(hours=8)))
                last_modified = cst_time.strftime('%Y-%m-%d %H:%M:%S')

            pdf_file = PyPDF2.PdfFileReader(io.BytesIO(raw_content))
            num_pages = pdf_file.numPages
            metadata = pdf_file.getDocumentInfo()
            text = ""
            for page_num in range(num_pages):
                page = pdf_file.getPage(page_num)
                text += page.extractText()

            return get_return_result(text, metadata, encoding, file_name, file_size, last_modified)
        else:
            raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                                   MyErrorCode.InvalidArgument.value,
                                   " 请求错误 ")
    except Exception as e:
        raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                               MyErrorCode.InvalidArgument.value,
                               e.__str__())


def get_return_result(file_content, metadata, encoding: str, file_name: str, file_size: int,
                      last_modified: str) -> FileParseResult:
    """ return the same result """
    regex_all, regex_all_statistical = RegexField(), RegexFieldStatistical()
    if file_content:
        regex_all, regex_all_statistical = get_regex_val(file_content)
    extra_field = ExtraField(
        date='',
        language='',
        charset='',
        subject=metadata.title if metadata.title else '',
        from_email='',
        to_email='',
        images=[],
        link=[],
    )
    return FileParseResult(file_size=file_size, file_name=file_name, last_modified=last_modified,
                           file_content=file_content, file_encoding=encoding,
                           regex_all=regex_all,
                           regex_all_statistical=regex_all_statistical, extra=extra_field)
