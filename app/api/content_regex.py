import re
from app.schemas.parse import RegexField, RegexFieldStatistical
from collections import OrderedDict, Counter


class RegexRules:
    def __init__(self, content: str):
        self.content = content

    def get_all(self) -> RegexField:
        phone_numbers = self.get_phone_numbers()
        emails = self.get_emails()
        addresses = self.get_addresses()
        company_names = self.get_company_names()
        countries = self.get_countries()
        land_line = self.get_land_line()
        return RegexField(
            phone_numbers=phone_numbers,
            emails=emails,
            addresses=addresses,
            company_names=company_names,
            countries=countries,
            land_line=land_line,

        )

    def get_value_statistics(self, l_origin: list) -> dict:
        """ Number of occurrences of statistical data """
        return dict(Counter(l_origin))

    def get_value_filter(self, l_origin: list) -> list:
        """ Remove duplicate and empty data """
        return list(OrderedDict.fromkeys(val for val in l_origin if val))

    def get_phone_numbers(self) -> list:
        regex = r'\b\d{11}\b'
        return re.findall(regex, self.content)

    def get_emails(self) -> list:
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        return re.findall(regex, self.content)

    def get_addresses(self) -> list:
        regex = r'\b\d{1,5}\s\w+\s\w+\b'
        return re.findall(regex, self.content)

    def get_company_names(self) -> list:
        regex = r'\b[A-Z][A-Za-z]+\s[A-Z][A-Za-z]+\b'
        return re.findall(regex, self.content)

    def get_countries(self) -> list:
        regex = r"\b[A-Z][a-z]+\b"
        return re.findall(regex, self.content)

    def get_land_line(self) -> list:
        regex = r"\b\d{3}-\d{3}-\d{4}\b"
        return re.findall(regex, self.content)

    def get_link(self):
        regex = r'<a[^>]+href=["\'](.*?)["\'][^>]*>'
        return re.findall(regex, self.content)

    def get_image(self):
        regex = r'<img[^>]+src=["\'](.*?)["\'][^>]*>'
        return re.findall(regex, self.content)


def get_regex_val(c: str):
    regexrules = RegexRules(c)

    regex_all_not_remove = regexrules.get_all()
    # 获取去重的数据
    regex_all = RegexField(
        phone_numbers=regexrules.get_value_filter(regex_all_not_remove.phone_numbers),
        emails=regexrules.get_value_filter(regex_all_not_remove.emails),
        addresses=regexrules.get_value_filter(regex_all_not_remove.addresses),
        company_names=regexrules.get_value_filter(regex_all_not_remove.company_names),
        countries=regexrules.get_value_filter(regex_all_not_remove.countries),
        land_line=regexrules.get_value_filter(regex_all_not_remove.land_line),
    )
    # 统计
    regex_all_statistical = RegexFieldStatistical(
        phone_numbers=regexrules.get_value_statistics(regex_all_not_remove.phone_numbers),
        emails=regexrules.get_value_statistics(regex_all_not_remove.emails),
        addresses=regexrules.get_value_statistics(regex_all_not_remove.addresses),
        company_names=regexrules.get_value_statistics(regex_all_not_remove.company_names),
        countries=regexrules.get_value_statistics(regex_all_not_remove.countries),
        land_line=regexrules.get_value_statistics(regex_all_not_remove.land_line),
    )
    return regex_all, regex_all_statistical
