from typing import Optional

import typesense
import pymysql
import os
from urllib.parse import urlparse
import pandas as pd
import datetime
from tqdm import tqdm
from app.db.init_typesense import client

tqdm.pandas()
import unicodedata
import re

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


collections = [
    {
        "name": "fb_post",
        "fields": [
            {"name": "source", "type": "string"},
            {"name": "url", "type": "string"},
            {"name": "text", "type": "string"},
            {"name": "text_convert", "type": "string"},
            {"name": "reactions", "type": "int32"},
            {"name": "comments", "type": "int32"},
            {"name": "likes", "type": "int32"},
            {"name": "ahah", "type": "int32"},
            {"name": "love", "type": "int32"},
            {"name": "wow", "type": "int32"},
            {"name": "sigh", "type": "int32"},
            {"name": "grrr", "type": "int32"},
            {"name": "grrr", "type": "int32"},
            {"name": "post_id", "type": "string"},
            {"name": "create_date", "type": "string"},
            {"name": "last_update", "type": "int64"},
        ],
        "default_sorting_field": "last_update",
    },
    {
        "name": "fb_comment",
        "fields": [
            {"name": "url", "type": "string"},
            {"name": "text", "type": "string"},
            {"name": "text_convert", "type": "string"},
            {"name": "reactions", "type": "int32"},
            {"name": "source", "type": "string"},
            {"name": "sentiment", "type": "string"},
            {"name": "post_id", "type": "string"},
            {"name": "create_date", "type": "string"},
            {"name": "last_update", "type": "int64"},
        ],
        "default_sorting_field": "last_update",
    },
]

try:
    create_response = client.collections.create(collections[0])
except typesense.exceptions.ObjectAlreadyExists:
    print("Object fb_post already create")

try:
    create_response = client.collections.create(collections[1])
except typesense.exceptions.ObjectAlreadyExists:
    print("Object fb_comment already create")

all_collection = {
    "name": "fb_all",
    "default_sorting_field": "last_update",
    "fields": [
        {"name": "last_update", "type": "int64"},
        {"name": "type", "type": "string"},
    ],
}

for collection in collections:
    for field in collection["fields"]:
        if field["name"] == "last_update":
            continue
        all_collection["fields"].append(
            {"name": f"{collection['name']}_{field['name']}", "type": field["type"]}
        )

try:
    create_response = client.collections.create(all_collection)
except typesense.exceptions.ObjectAlreadyExists:
    print("Object fb_all already create")

cursor = init_cursor(os.getenv("DATABASE_URL"))
sql = "SELECT * FROM fb_post"
cursor.execute(sql)
df_database_post = cursor.fetchall()
df_database_post = pd.DataFrame(df_database_post)
print(df_database_post.head())

sql = "SELECT * FROM fb_comment"
cursor.execute(sql)
df_database_comment = cursor.fetchall()
df_database_comment = pd.DataFrame(df_database_comment)
print(df_database_comment.head())

df_database_post["last_update"] = df_database_post.last_update.progress_apply(
    lambda x: int(datetime.datetime.timestamp(x) if type(x) != str else int(datetime.datetime.now().timestamp()))
)
df_database_post[["reactions"]] = df_database_post[["reactions"]].fillna(value=0)
df_database_post["create_date"] = df_database_post.create_date.progress_apply(
    lambda x: str(x)
)
df_database_post["reactions"] = df_database_post.reactions.progress_apply(
    lambda x: int(x)
)
df_database_post["text_convert"] = df_database_post.text.progress_apply(
    lambda x: convert_accented_vietnamese_text(x) if type(x) == str else ""
)

print(df_database_post.head())
df_database_comment.dropna(subset=["last_update"], inplace=True)
df_database_comment["last_update"] = df_database_comment.last_update.progress_apply(
    lambda x: int(datetime.datetime.timestamp(x))
)
df_database_comment["id"] = df_database_comment["comment_id"]
df_database_comment["create_date"] = df_database_comment.create_date.progress_apply(
    lambda x: str(x)
)
df_database_comment[["reactions"]] = df_database_comment[["reactions"]].fillna(value=0)
df_database_comment["reactions"] = df_database_comment.reactions.progress_apply(
    lambda x: int(x)
)

df_database_comment["text_convert"] = df_database_comment.text.progress_apply(
    lambda x: convert_accented_vietnamese_text(x) if type(x) == str else ""
)
print(df_database_comment.head())

fb_posts_sql = df_database_post.to_dict("records")
fb_comment_sql = df_database_comment.to_dict("records")
fb_all_sql = []
for i in fb_posts_sql:
    temp_i = {}
    temp_i["id"] = i["id"]
    for k, v in i.items():
        if k != "last_update":
            temp_k = f"fb_post_{k}"
        else:
            temp_k = k
        temp_i[temp_k] = v
    temp_i["type"] = "fb_post"

    for field in collections[1]["fields"]:
        if field["name"] == "last_update":
            continue
        if field["type"] == "int32":
            temp_i[f"{collections[1]['name']}_{field['name']}"] = 0
        else:
            temp_i[f"{collections[1]['name']}_{field['name']}"] = ""

    fb_all_sql.append(temp_i)

for i in fb_comment_sql:
    temp_i = {}
    temp_i["id"] = i["id"]
    for k, v in i.items():
        if k != "last_update":
            temp_k = f"fb_comment_{k}"
        else:
            temp_k = k
        temp_i[temp_k] = v
    temp_i["type"] = "fb_comment"
    for field in collections[0]["fields"]:
        if field["name"] == "last_update":
            continue
        if field["type"] == "int32":
            temp_i[f"{collections[0]['name']}_{field['name']}"] = 0
        else:
            temp_i[f"{collections[0]['name']}_{field['name']}"] = ""

    fb_all_sql.append(temp_i)
print(len(fb_comment_sql))
print(fb_all_sql[0])
client.collections["fb_post"].documents.import_(fb_posts_sql, {"action": "upsert"})
client.collections["fb_comment"].documents.import_(fb_comment_sql, {"action": "upsert"})
client.collections["fb_all"].documents.import_(fb_all_sql, {"action": "upsert"})
