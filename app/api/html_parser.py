import os
import datetime
import requests

from app.schemas.const import MyErrorCode, HttpStatusCode
from app.schemas.parse import FileParseResult, RegexField, RegexFieldStatistical, ExtraField
from app.utils.app_exceptions import UnicornException
from app.api.content_regex import get_regex_val
from bs4 import BeautifulSoup
from collections import OrderedDict


def parse_local_html_file(file_path):
    """
    解析本地的html、htm文件内容
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
            file_content = file.read()
        return get_return_result(file_content, file_size, file_name, last_modified, encoding)
    except Exception as e:
        raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                               MyErrorCode.InvalidArgument.value,
                               e.__str__())


def parse_remote_html_file(file_url):
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

            return get_return_result(raw_content, file_size, file_name, last_modified="", encoding=encoding)
        else:
            raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                                   MyErrorCode.InvalidArgument.value,
                                   " 请求错误 ")
    except Exception as e:
        raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                               MyErrorCode.InvalidArgument.value,
                               e.__str__())


def get_html_images(soup):
    images = []
    for img_tag in soup.find_all("img"):
        img_src = img_tag.get("src")
        if img_src:
            images.append(img_src)
    return list(OrderedDict.fromkeys(val for val in images if val))


def get_html_links(soup):
    links = []
    for link_tag in soup.find_all("a"):
        link_href = link_tag.get("href")
        if link_href and not link_href.startswith('#'):
            links.append(link_href)
    return list(OrderedDict.fromkeys(val for val in links if val))


def get_return_result(file_content, file_size, file_name, last_modified, encoding):
    soup = BeautifulSoup(file_content, 'html.parser')

    file_img = get_html_images(soup)
    file_link = get_html_links(soup)
    last_modified_c = soup.find("meta", attrs={"http-equiv": "last-modified"})
    last_modified_c = last_modified_c["content"] if last_modified_c else ""
    # 获取标题
    title = soup.title.string
    # 获取 body 内容
    file_content = soup.get_text()
    # 语言
    language = soup.find("html")["lang"] if soup.find("html") and "lang" in soup.find("html").attrs else ""
    # Get encoding format
    charset = soup.find("meta")["charset"] if soup.find("meta") and "charset" in soup.find("meta").attrs else ""

    regex_all, regex_all_statistical = RegexField(), RegexFieldStatistical()
    if file_content:
        regex_all, regex_all_statistical = get_regex_val(file_content)

    extra_field = ExtraField(
        date=last_modified_c,
        language=language,
        charset=charset,
        subject=title,
        images=file_img,
        link=file_link,
    )

    return FileParseResult(file_size=file_size, file_name=file_name, last_modified=last_modified,
                           file_content=file_content, file_encoding=encoding,
                           regex_all=regex_all, regex_all_statistical=regex_all_statistical, extra=extra_field)
