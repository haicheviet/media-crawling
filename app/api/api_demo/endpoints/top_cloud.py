from typing import List
from datetime import datetime
from app.core.decorator import decorator_logger_info
from app.utils import convert_accented_vietnamese_text
from fastapi import APIRouter
from starlette.requests import Request
from pydantic import BaseModel
from app.core.wrapper_threading import ThreadWithReturnValue
# from underthesea import word_tokenize
from collections import Counter, defaultdict
from enum import Enum
from app.db.init_typesense import client



router = APIRouter()

current_time_stamp = int(datetime.now().timestamp())

LIMIT_WORD = 30


class SourceTopicWord(str, Enum):
    fb_comment = "fb_comment"
    fb_post = "fb_post"
    fb_all = "fb_all"
    news = "news"
    source_all = "all"


with open("stopwords.txt", "r") as f:
    stop_words = f.read().splitlines()

import re


def strip_emoji(text):
    RE_EMOJI = re.compile(
        "([\U00002600-\U000027BF])|([\U0001f300-\U0001f64F])|([\U0001f680-\U0001f6FF])"
    )
    return RE_EMOJI.sub(r"", text)


def preprocess_word(text):
    if not text:
        return None
    text = strip_emoji(text)
    if text == "":
        return None
    return text


def remove_redundant_word(token):
    if len(token) < 4 and len(token.split()) == 1:
        return ""
    elif len(token.split()) < 2:
        return ""
    if token in stop_words:
        return ""
    return token.lower()


# def count_token_word(text):
#     comment_words_process = list(map(lambda x: preprocess_word(x), text))
#     comment_words_process = list(filter(None, comment_words_process))
#     list_token_word = [word_tokenize(i) for i in comment_words_process]
#     list_token_word = [remove_redundant_word(j) for i in list_token_word for j in i]
#     list_token_word = list(filter(lambda x: x.strip() != "", list_token_word))
#     word_count_dict = Counter(list_token_word)
#     return word_count_dict


class KeywordCount(BaseModel):
    keyword: str
    occurrence: int


class ResponseTopicCloud(BaseModel):
    topic_cloud: List[KeywordCount]


@router.get("/generateTopicCloud", response_model=ResponseTopicCloud)
@decorator_logger_info
def generate_topic_cloud(
    request: Request,
    keyword: str,
    begin_date_timestamp: int = 0,
    end_date_timestamp: int = 0,
    source_crawl: SourceTopicWord = SourceTopicWord.source_all,
):
    keyword = convert_accented_vietnamese_text(keyword)
    search_parameters_fb_post = {}
    search_parameters_fb_comment = {}
    search_parameters_news = {}
    search_parameters = {"q": keyword, "num_typos": 1, "per_page": 250}
    count_total = defaultdict(int)

    if begin_date_timestamp:
        if not end_date_timestamp:
            search_parameters.update(
                {"filter_by": f"last_update:<={end_date_timestamp}"}
            )
        else:
            search_parameters.update(
                {
                    "filter_by": f"last_update:<={end_date_timestamp} && last_update:>={begin_date_timestamp}"
                }
            )
    search_parameters_fb_post = dict(
        {"query_by": "text_convert", "include_fields": "last_update,text,text_convert"},
        **search_parameters,
    )
    search_parameters_fb_comment = dict(
        {
            "query_by": "text_convert",
            "include_fields": "last_update,text,text_convert",
        },
        **search_parameters,
    )
    search_parameters_news = dict(
        {
            "query_by": "title_convert,keyword_convert",
            "include_fields": "last_update,keyword,summary,title_convert,keyword_convert",
        },
        **search_parameters,
    )
    if (
        source_crawl == SourceTopicWord.source_all
        or source_crawl == SourceTopicWord.news
    ):
        thread_news = ThreadWithReturnValue(
            target=client.collections["news"].documents.search,
            args=(search_parameters_news,),
        )
        thread_news.start()
    else:
        thread_news = None

    if (
        source_crawl == SourceTopicWord.source_all
        or source_crawl == SourceTopicWord.fb_all
        or source_crawl == SourceTopicWord.fb_post
    ):
        thread_fb_post = ThreadWithReturnValue(
            target=client.collections["fb_post"].documents.search,
            args=(search_parameters_fb_post,),
        )
        thread_fb_post.start()
    else:
        thread_fb_post = None

    if (
        source_crawl == SourceTopicWord.source_all
        or source_crawl == SourceTopicWord.fb_all
        or source_crawl == SourceTopicWord.fb_comment
    ):
        thread_fb_comment = ThreadWithReturnValue(
            target=client.collections["fb_comment"].documents.search,
            args=(search_parameters_fb_comment,),
        )
        thread_fb_comment.start()
    else:
        thread_fb_comment = None
    if thread_news:
        query_return_news = thread_news.join()
        text_news = [
            i["document"]["keyword"].split(";")
            for i in query_return_news.get("hits", [])
        ]
        text_news.extend(
            [
                i["document"]["summary"].split(";")
                for i in query_return_news.get("hits", [])
            ]
        )
        text_news = [j for i in text_news for j in i]
        text_token_news = list(map(lambda x: x.strip().lower(), text_news))
        text_token_news = list(filter(lambda x: x != "", text_token_news))
        count_news = Counter(text_token_news).most_common(LIMIT_WORD)
        for item in count_news:
            count_total[item[0]] += item[1]
    if thread_fb_post or thread_fb_comment:
        text_fb = []
        if thread_fb_post:
            query_return_fb_post = thread_fb_post.join()
            text_fb.extend(
                [i["document"]["text"] for i in query_return_fb_post.get("hits", [])]
            )
        if thread_fb_comment:
            query_return_fb_comment = thread_fb_comment.join()
            text_fb.extend(
                [i["document"]["text"] for i in query_return_fb_comment.get("hits", [])]
            )
        count_fb = []
        # count_fb = count_token_word(text_fb).most_common(LIMIT_WORD)
        for item in count_fb:
            count_total[item[0]] += item[1]

    result = [
        {"keyword": k, "occurrence": v}
        for k, v in sorted(count_total.items(), key=lambda item: item[1], reverse=True)[
            :LIMIT_WORD
        ]
    ]
    return {"topic_cloud": result}
