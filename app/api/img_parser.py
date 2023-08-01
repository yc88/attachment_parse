import os

import requests

from app.schemas.const import MyErrorCode, HttpStatusCode
from app.schemas.parse import FileParseResult
from app.utils.app_exceptions import UnicornException
from app.api.content_regex import RegexRules, get_regex_val
from app.schemas.parse import RegexField, RegexFieldStatistical, ExtraField
import email
from datetime import datetime, timezone, timedelta
from io import BytesIO
from PIL import Image
import pytesseract


def parse_local_image_file(file_path, tesseract_path: str, lang: str = None):
    """
    解析本地的image文件内容
    """
    try:
        encoding = 'utf-8'
        # 获取文件名称
        file_name = os.path.basename(file_path)
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        # 获取最后修改时间
        last_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        img = Image.open(file_path)
        return get_return_result(img, encoding, file_name, file_size, last_modified)
    except Exception as e:
        raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                               MyErrorCode.InvalidArgument.value,
                               e.__str__())


def parse_remote_image_file(file_url, tesseract_path: str, lang: str = None):
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

            img = Image.open(BytesIO(raw_content))
            return get_return_result(img, encoding, file_name, file_size, last_modified,
                                     tesseract_path, lang)
        else:
            raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                                   MyErrorCode.InvalidArgument.value,
                                   " 请求错误 ")
    except Exception as e:
        raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                               MyErrorCode.InvalidArgument.value,
                               e.__str__())


def get_return_result(img, encoding: str, file_name: str, file_size: int,
                      last_modified: str, tesseract_path: str, lang: str = None) -> FileParseResult:
    """ return the same result """
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    # lan = pytesseract.pytesseract.get_languages()
    # lang = "+".join(lan)
    # 配置 pytesseract 支持的所有语言（可根据需要添加或删除语言）
    # custom_config = r'--oem 3 --psm 6 -l all'  # --oem 3 表示默认 OCR 引擎，--psm 6 表示解析整个块文本，-l all 表示使用所有语言
    file_content = pytesseract.image_to_string(img, lang=lang, config=r'--psm 6')
    regex_all, regex_all_statistical = ExtraField(), RegexFieldStatistical()
    if file_content:
        regex_all, regex_all_statistical = get_regex_val(file_content)
    extra_field = ExtraField(
        date='',
        language='',
        charset='',
        subject='',
        from_email='',
        to_email='',
        images=[],
        link=[],
    )
    return FileParseResult(file_size=file_size, file_name=file_name, last_modified=last_modified,
                           file_content=file_content, file_encoding=encoding,
                           regex_all=regex_all,
                           regex_all_statistical=regex_all_statistical, extra=extra_field)
