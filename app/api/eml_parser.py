import os
import requests

from app.schemas.const import MyErrorCode, HttpStatusCode
from app.schemas.parse import FileParseResult
from app.utils.app_exceptions import UnicornException
from app.api.content_regex import RegexRules, get_regex_val
from app.schemas.parse import RegexField, RegexFieldStatistical, ExtraField
import email
from email.header import decode_header
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from collections import OrderedDict, Counter


def parse_local_eml_file(file_path):
    """
    解析本地的eml文件内容
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
            msg = email.message_from_binary_file(file)

        return get_return_result(msg, encoding, file_name, file_size, last_modified)
    except Exception as e:
        raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                               MyErrorCode.InvalidArgument.value,
                               e.__str__())


def parse_remote_eml_file(file_url):
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

            msg = email.message_from_bytes(raw_content)

            return get_return_result(msg, encoding, file_name, file_size, last_modified)
        else:
            raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                                   MyErrorCode.InvalidArgument.value,
                                   " 请求错误 ")
    except Exception as e:
        raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                               MyErrorCode.InvalidArgument.value,
                               e.__str__())


def get_return_result(msg, encoding: str, file_name: str, file_size: int, last_modified: str) -> FileParseResult:
    """ return the same result """
    # 获取邮件标题
    subject = decode_subject(msg['Subject'])

    file_img = get_email_content_image(msg, encoding)
    file_link = get_email_content_link(msg, encoding)
    file_content = get_email_content(msg, encoding)

    # 语言
    language = msg.get("Content-Language", "")
    # 时间
    date = msg.get('Date')
    # 发送者
    from_email = msg.get('From')
    if from_email:
        from_email = RegexRules(from_email).get_emails()[0]
    # 接收者
    to_email = msg.get('To')
    charset = msg.get_content_charset()
    regex_all, regex_all_statistical = RegexField(), RegexFieldStatistical()
    if file_content:
        regex_all, regex_all_statistical = get_regex_val(file_content + to_email + ' ' + from_email)
    if charset is not str:
        charset = str(charset)
    extra_field = ExtraField(
        date=date,
        language=language,
        charset=charset,
        subject=subject,
        from_email=from_email,
        to_email=to_email,
        images=file_img,
        link=file_link,
    )

    if from_email:
        regex_all.emails.append(from_email)
        regex_all_statistical.emails.__setitem__(from_email, 1)
    if to_email:
        regex_all.emails.append(to_email)
        regex_all_statistical.emails.__setitem__(to_email, 1)

    return FileParseResult(file_size=file_size, file_name=file_name, last_modified=last_modified,
                           file_content=file_content, file_encoding=encoding,
                           regex_all=regex_all,
                           regex_all_statistical=regex_all_statistical, extra=extra_field)


def get_email_content(msg, encoding: str):
    """ get content """
    content = ""
    for part in msg.walk():
        content_type = part.get_content_type()
        if content_type == 'text/plain':
            content += part.get_payload(decode=True).decode(encoding)
    return content


def decode_subject(subject):
    """ get subject """
    decoded_subject = []
    for value, encoding in decode_header(subject):
        if isinstance(value, bytes):
            if encoding is None:
                decoded_subject.append(value.decode('utf-8'))
            else:
                decoded_subject.append(value.decode(encoding))
        else:
            decoded_subject.append(value)
    return ' '.join(decoded_subject)


def get_email_content_image(msg, encoding: str):
    """ get all image """
    # 获取图片附件
    images = []
    text_content = []
    for part in msg.walk():
        content_type = part.get_content_type()
        if content_type.startswith('image/'):
            images.append(part.get_payload(decode=True))
        elif content_type == "text/html":
            text_content.append(part.get_payload(decode=True).decode(encoding))
    soup = BeautifulSoup("".join(text_content), "html.parser")
    images += [img["src"] for img in soup.find_all("img", src=True)]
    return list(OrderedDict.fromkeys(val for val in images if val))


def get_email_content_link(msg, encoding: str):
    """ get all link """
    # 获取图片附件
    link = []
    text_content = []
    for part in msg.walk():
        content_type = part.get_content_type()
        if content_type.startswith('a/'):
            link.append(part.get_payload(decode=True))
        elif content_type == "text/html":
            text_content.append(part.get_payload(decode=True).decode(encoding))
    soup = BeautifulSoup("".join(text_content), "html.parser")
    link += [img["src"] for img in soup.find_all("a", src=True)]
    return list(OrderedDict.fromkeys(val for val in link if val))
