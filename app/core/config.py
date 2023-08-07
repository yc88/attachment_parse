import json

from pydantic_settings import BaseSettings
from app.schemas.const import File_Cache_Dist
import requests


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
