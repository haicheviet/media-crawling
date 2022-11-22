from typing import Optional


import unicodedata
import re
from urllib.parse import urlparse
import pymysql

VIETNAMESE_PATTERN = {
    "[àáảãạăắằẵặẳâầấậẫẩ]": "a",
    "[đ]": "d",
    "[èéẻẽẹêềếểễệ]": "e",
    "[ìíỉĩị]": "i",
    "[òóỏõọôồốổỗộơờớởỡợ]": "o",
    "[ùúủũụưừứửữự]": "u",
    "[ỳýỷỹỵ]": "y",
}


def convert_accented_vietnamese_text(data: Optional[str]) -> str:
    if not data:
        return ""
    data = data.lower()
    data = unicodedata.normalize("NFC", data)
    for regex, replace in VIETNAMESE_PATTERN.items():
        data = re.sub(regex, replace, data)

    data = data.replace("\n", " ")
    return data


def init_cursor(database_url, write_transaction=False):
    database_url = urlparse(database_url)
    connection = pymysql.connect(
        host=database_url.hostname,
        user=database_url.username,
        password=database_url.password,
        db=database_url.path[1:],
        port=database_url.port,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    cursor = connection.cursor()
    if write_transaction:
        return cursor, connection
    return cursor