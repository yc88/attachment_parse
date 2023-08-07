from app.utils.app_exceptions import UnicornException
from app.schemas.const import MyErrorCode, HttpStatusCode, Allowed_Extensions
import os
import requests
from app.api.txt_parser import parse_local_text_file, parse_remote_text_file
from app.api.eml_parser import parse_local_eml_file, parse_remote_eml_file
from app.api.html_parser import parse_local_html_file, parse_remote_html_file
from app.api.xml_parser import parse_local_xml_file, parse_remote_xml_file
from app.api.xls_parser import parse_local_xls_file, parse_remote_xls_file
from app.api.docx_parser import parse_local_docx_file, parse_remote_docx_file
from app.api.csv_parser import parse_local_csv_file, parse_remote_csv_file
from app.api.pdf_parser import parse_local_pdf_file, parse_remote_pdf_file
from app.api.ppt_parser import parse_local_ppt_file, parse_remote_ppt_file
from app.api.img_parser import parse_local_image_file, parse_remote_image_file
from app.core.config import Settings, GetFileJson


class FileParser:

    def __init__(self, path_url: str, is_local: bool, settings: Settings):
        self.path = path_url
        self.is_local = is_local
        self.setting = settings

    async def read_file(self):
        if self.path == "":
            raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                                   MyErrorCode.InvalidArgument.value, "path not empty")
        extension = ""
        file_name = ""
        if self.is_local:
            if not os.path.isfile(self.path):
                raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                                       MyErrorCode.InvalidArgument.value, "Please  enter a local file path")
            if not os.path.exists(self.path):
                raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                                       MyErrorCode.InvalidArgument.value, " file path  Not found ")
            file_name = os.path.split(self.path)[1]
            extension = os.path.splitext(self.path)[1]
        else:
            if not self.is_remote_file_exists():
                raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                                       MyErrorCode.InvalidArgument.value, "Please  enter the remote file path")
            file_name = self.get_remote_file_name()
            extension = self.get_remote_file_extension()
        if extension == "" or file_name == "":
            raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                                   MyErrorCode.InvalidArgument.value, " get file extension fail ")
        if str.lower(extension) not in Allowed_Extensions:
            raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                                   MyErrorCode.InvalidArgument.value, " This type of file is not currently supported ")
        ext = str.lower(extension)
        if ext:
            match str.lower(extension):
                case '.txt':
                    if self.is_local:
                        return parse_local_text_file(self.path)
                    else:
                        return parse_remote_text_file(self.path)
                case '.docx':
                    # none
                    if self.is_local:
                        return parse_local_docx_file(self.path)
                    else:
                        return parse_remote_docx_file(self.path)
                case '.doc':
                    # none
                    raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                                           MyErrorCode.Unimplemented.value,
                                           " the doc type not parse ")
                case '.xls' | '.xlsx':
                    if self.is_local:
                        return parse_local_xls_file(self.path)
                    else:
                        return parse_remote_xls_file(self.path)
                case '.csv':
                    if self.is_local:
                        return parse_local_csv_file(self.path)
                    else:
                        return parse_remote_csv_file(self.path)
                case '.ppt' | '.pptx':
                    if self.is_local:
                        return parse_local_ppt_file(self.path, self.setting.tesseract_cmd_path,
                                                    self.setting.tesseract_languages)
                    else:
                        return parse_remote_ppt_file(self.path, self.setting.tesseract_cmd_path,
                                                     self.setting.tesseract_languages)
                case '.png' | '.jpg' | '.jpeg' | '.gif':
                    if self.is_local:
                        return parse_local_image_file(self.path,
                                                      self.setting.tesseract_cmd_path, self.setting.tesseract_languages)
                    else:
                        return parse_remote_image_file(self.path, self.setting.tesseract_cmd_path,
                                                       self.setting.tesseract_languages)
                case '.pdf':
                    if self.is_local:
                        return parse_local_pdf_file(self.path)
                    else:
                        return parse_remote_pdf_file(self.path)
                case '.html' | '.htm':
                    if self.is_local:
                        return parse_local_html_file(self.path)
                    else:
                        return parse_remote_html_file(self.path)
                case '.eml':
                    if self.is_local:
                        return parse_local_eml_file(self.path)
                    else:
                        return parse_remote_eml_file(self.path)
                case '.xml':
                    if self.is_local:
                        return parse_local_xml_file(self.path)
                    else:
                        return parse_remote_xml_file(self.path)
                case _:
                    raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                                           MyErrorCode.InvalidArgument.value,
                                           " This type of file is not currently supported ")
        else:
            raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                                   MyErrorCode.InvalidArgument.value,
                                   " get extension fail ")

    def is_remote_file_exists(self):
        try:
            response_result = requests.head(self.path)
            return response_result.status_code == 200
        except Exception as e:
            raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                                   MyErrorCode.InvalidArgument.value,
                                   e.__str__())

    def get_remote_file_name(self):
        try:
            response_result = requests.get(self.path)
            if response_result.status_code == HttpStatusCode.HTTP_200_OK:
                file_name = self.path.split('/')[-1]
                return file_name
            else:
                return ""
        except Exception as e:
            raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                                   MyErrorCode.InvalidArgument.value,
                                   e.__str__())

    def get_remote_file_extension(self):
        try:
            response_result = requests.get(self.path)
            if response_result.status_code == HttpStatusCode.HTTP_200_OK:
                file_name = os.path.splitext(self.path)[1]
                return file_name
            else:
                return ""
        except Exception as e:
            raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                                   MyErrorCode.InvalidArgument.value,
                                   e.__str__())
