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
import xml.etree.ElementTree as ET
import re


def parse_local_xml_file(file_path):
    """
    解析本地的xml文件内容
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

        tree = ET.parse(file_path)
        root = tree.getroot()
        return get_return_result(root, file_size, file_name, last_modified, encoding)
    except Exception as e:
        print(e)
        raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                               MyErrorCode.InvalidArgument.value,
                               e.__str__())


def parse_remote_xml_file(file_url):
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
            root = ET.fromstring(raw_content)
            return get_return_result(root, file_size, file_name, last_modified="", encoding=encoding)
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


def get_return_result(root, file_size, file_name, last_modified, encoding):
    data, file_content = get_recursive_content(root)
    data = {root.tag: data}
    file_content_struct = json.dumps(data)
    regex_all, regex_all_statistical = get_regex_val(file_content)
    title = root.find(".//title")
    if not title:
        title = ""
    lastmod = root.find(".//lastmod")
    if not lastmod:
        lastmod = ""
    charset = root.get("encoding")
    if not charset:
        charset = ""
    language = root.get('{http://www.w3.org/XML/1998/namespace}lang')
    if not language:
        language = ""
    extra_field = ExtraField(
        date=lastmod,
        language=language,
        charset=charset,
        subject=title,
        images=[],
        link=[],
        content_struct=file_content_struct
    )
    return FileParseResult(file_size=file_size, file_name=file_name, last_modified=last_modified,
                           file_content=file_content, file_encoding=encoding,
                           regex_all=regex_all, regex_all_statistical=regex_all_statistical, extra=extra_field)


def get_recursive_content(root):
    data = []
    data_content = ""
    for element in root:
        item = {}
        for child_element in element:
            if len(child_element) > 0:
                item[child_element.tag], content = get_recursive_content(child_element)
                data_content += " \n " + content
            else:
                item[child_element.tag] = child_element.text
                data_content += " \n" + child_element.text
        data.append({element.tag: item})
    return data, data_content
