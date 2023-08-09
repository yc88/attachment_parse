import re
from app.schemas.parse import RegexField, RegexFieldStatistical
from app.core.config import Settings, GetFileJson
from collections import OrderedDict, Counter


class RegexRules:
    def __init__(self, content: str, setting: Settings = None):
        self.content = content
        if setting:
            self.setting = setting
        else:
            self.setting = Settings()
        get_json = GetFileJson(self.setting)
        self.countries_map, self.countries_regex = get_json.get_countries()
        self.organizations_map, self.result_organizations_regex, self.organizations_regex = get_json.get_organizations()

    def get_all(self) -> RegexField:
        phone_numbers = self.get_phone_numbers()
        emails = self.get_emails()
        addresses = self.get_addresses()
        countries = self.get_countries()
        land_line = self.get_land_line()
        get_link = self.get_link()
        company_names = self.get_organizations(emails, get_link)
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
        regex = r"[0-9a-zA-Z ,.-]+, [0-9a-zA-Z ,.-]+, [0-9a-zA-Z ,.-]+, [0-9a-zA-Z]+"
        return re.findall(regex, self.content, re.IGNORECASE)

    def get_organizations(self, emails: list, links: list):
        """获取当前文档的组织结构数据"""
        result = self.get_content_organizations()
        result_email = self.get_email_organizations(emails)
        result_link = self.get_link_organizations(links)
        return [v for v in result.union(result_email, result_link)]

    def get_email_organizations(self, emails: list) -> set:
        """通过对应的正则取匹配邮箱"""
        txt = ','.join(emails)
        # 提取邮箱域名的更精细匹配
        domain_pattern = r'@([A-Za-z0-9-]+\.[A-Za-z0-9.-]+\.[A-Za-z]{2,})|@([A-Za-z0-9-]+\.[A-Za-z0-9.-]+)'
        domain_matches = [match[0] or match[1] for match in re.findall(domain_pattern, txt)]
        return self.get_regex_organizations(','.join(domain_matches))

    def get_link_organizations(self, link: list) -> set:
        """通过对应的正则取匹配连接"""
        result = set()
        if link:
            result = self.get_regex_organizations(','.join(link))
        return result

    def get_content_organizations(self):
        """通过全名获取内容里面的机构"""
        result = set()
        regex = self.organizations_regex
        if regex:
            data = re.findall(regex, self.content, re.IGNORECASE)
            for k in [match for sublist in data for match in sublist]:
                if k:
                    v = self.countries_map.get(k)
                    if v:
                        result.add(v)
        return result

    def get_regex_organizations(self, content_str: str):
        "通过正则取匹配查找对应的机构"
        result = set()
        if content_str:
            regex_dist = self.result_organizations_regex
            if regex_dist:
                for regex in regex_dist:
                    if re.search(regex, content_str):
                        result.add(regex_dist[regex])
        return result

    def get_email_suffix(self, emails: list):
        """获取邮箱的@符合后面的数据字符"""
        if emails:
            txt = ','.join(emails)
            # 提取邮箱域名的更精细匹配
            domain_pattern = r'@([A-Za-z0-9-]+\.[A-Za-z0-9.-]+\.[A-Za-z]{2,})|@([A-Za-z0-9-]+\.[A-Za-z0-9.-]+)'
            return [match[0] or match[1] for match in re.findall(domain_pattern, txt)]

    def get_email_detail_str(self, emails: list):
        """获取邮箱的@符合后面字符，并且以.分割更细"""
        if emails:
            pattern = r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b"
            domain_parts = set()
            for email in emails:
                match = re.search(pattern, email)
                if match:
                    domain = match.group(1)
                    domain_parts.update(domain.split("."))
            return [v for v in domain_parts]

    def get_countries(self) -> list:
        result = []
        regex = self.countries_regex
        if regex:
            data = re.findall(regex, self.content, re.IGNORECASE)
            for k in [match for sublist in data for match in sublist]:
                if k:
                    v = self.countries_map.get(k)
                    if v:
                        result.append(v)
        return result

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
