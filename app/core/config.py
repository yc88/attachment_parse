import json

from pydantic_settings import BaseSettings
from app.schemas.const import File_Cache_Dist
import requests
from app.utils.app_exceptions import UnicornException
from app.schemas.const import MyErrorCode, HttpStatusCode


class Settings(BaseSettings):
    app_name: str = "attachment parse"
    tesseract_cmd_path: str = ''
    tesseract_languages: str = ''
    minio_path: str = ''
    cache_dir: str = ''

    class Config:
        env_file = '.env'


class GetFileJson:
    def __init__(self, setting: Settings):
        self.setting = setting

    def get_countries(self):
        """获取对应的国家匹配字符串"""
        url = self.setting.minio_path + self.setting.cache_dir + File_Cache_Dist["countries"]
        res = requests.get(url)
        result_countries = {}
        regex = ''
        if res.status_code == 200:
            content = res.content
            dict_data = json.loads(content.decode('utf-8'))
            result = []
            if dict_data:
                for v in dict_data:
                    key = v["key"]
                    val = v["value"]
                    if key and val:
                        result_countries[val] = key
                        result.append(val)
            if result:
                regex = r"(" + '|'.join(result) + ")"
            return result_countries, regex
        else:
            return result_countries, regex

    def get_organizations(self):
        """获取对应的国家匹配字符串"""
        try:
            url = self.setting.minio_path + self.setting.cache_dir + File_Cache_Dist["organizations"]
            res = requests.get(url)
            result_organizations = {}
            regex = ''
            result_organizations_regex = {}
            if res.status_code == 200:
                content = res.content
                dict_data = json.loads(content.decode('utf-8'))
                result = []
                if dict_data:
                    for v in dict_data:
                        key = v["key"]  # id
                        val = v["value"]  # full_name
                        regex_str = v["regex_str"]
                        if key and val:
                            result_organizations[val] = key
                            result.append(val)
                        if key and regex_str:
                            result_organizations_regex[r"(" + regex_str + ")"] = key
                print(result_organizations, result_organizations_regex, regex)
                if result:
                    regex = r"(" + '|'.join(result) + ")"
                return result_organizations, result_organizations_regex, regex
            else:
                return result_organizations, result_organizations_regex, regex
        except Exception as e:
            raise UnicornException(HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                                   MyErrorCode.InvalidArgument.value,
                                   e.__str__())
