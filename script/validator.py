import re

class Validator:
    @staticmethod
    def validate_tunnel(entry) -> bool:
        value = entry.get().strip()
        if re.match(r'^[A-Za-z0-9.-]+$', value):  #允许字母数字和域名符号
            entry.state(["!invalid"])
            return True
        entry.state(["invalid"])
        return False

    @staticmethod
    def validate_port(entry) -> bool:
        value = entry.get().strip()
        if value.isdigit():
            entry.state(["!invalid"])
            return True
        entry.state(["invalid"])
        return False
