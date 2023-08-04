import pycountry

from app.utils.app_exceptions import UnicornException, app_exception_handler
from app.schemas.parse import ResponseModel
from app.core.config import Settings
import iso639
import pycountry


class Base:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def language(self):
        language_list = self.get_iso639_language()
        res = ResponseModel(success=False, data=language_list, code=0, message="")
        return res.get_dump()

    def get_iso639_language(self):
        language_list = []
        for code, language_info in iso639.languages.part1.items():
            language = {
                "language": language_info.name,
                "english_name": language_info.bibliographic,
                "chinese_name": language_info.terminology,
                "code": code
            }
            language_list.append(language)
        return language_list

    def get_pycountry_language(self):
        """效果不佳"""
        all_languages = []
        for lang in pycountry.languages:
            language_info = {
                "English Name": lang.name,
                "Alpha-2 Code": lang.alpha_3,
                "Alpha-3 Code": lang.alpha_3,
                "scope": lang.scope,
                "type": lang.type,
            }
            all_languages.append(language_info)
        return all_languages

