from typing import Dict, List
from datetime import datetime, timedelta
from app.core.decorator import decorator_logger_info
from app.utils import convert_accented_vietnamese_text
from fastapi import APIRouter
from starlette.requests import Request
from pydantic import BaseModel
from app.core.wrapper_threading import ThreadWithReturnValue
from app.db.init_typesense import client
router = APIRouter()

current_time_stamp = int(datetime.now().timestamp())


class SentimentAnalyst(BaseModel):
    neutral: int
    positive: int
    negative: int


class CountKeyWord(BaseModel):
    begin_date: int
    end_date: int
    fb_post: int
    fb_comment: int
    news: int
    sentiment_analyst: SentimentAnalyst


class ResponseCountKeyword(BaseModel):
    response: List[CountKeyWord]


@router.get("/countKeyword", response_model=ResponseCountKeyword)
@decorator_logger_info
def count_keyword(
    request: Request,
    keyword: str,
    begin_date_timestamp: int = 0,
    range_day_display: int = 7,
    time_frame_hour: int = 12,
):
    keyword = convert_accented_vietnamese_text(keyword)

    search_parameters_fb_post = {
        "q": keyword,
        "include_fields": "last_update",
        "num_typos": 1,
    }
    search_parameters_fb_comment = {
        "q": keyword,
        "include_fields": "last_update,sentiment",
        "num_typos": 1,
    }
    search_parameters_news = {
        "q": keyword,
        "include_fields": "last_update",
        "num_typos": 1,
    }

    if not begin_date_timestamp:
        begin_date_timestamp = int(
            (datetime.now() - timedelta(days=range_day_display)).timestamp()
        )
    begin_bin_date_timestamp = int(
        (datetime.now() - timedelta(hours=time_frame_hour)).timestamp()
    )

    end_bin_date_timestamp = current_time_stamp
    result = {"response": []}
    while begin_bin_date_timestamp >= begin_date_timestamp:
        search_parameters_fb_post.update(
            {
                "filter_by": f"last_update:<={end_bin_date_timestamp} && last_update:>={begin_bin_date_timestamp}",
                "query_by": "text_convert",
            }
        )
        search_parameters_fb_comment.update(
            {
                "filter_by": f"last_update:<={end_bin_date_timestamp} && last_update:>={begin_bin_date_timestamp}",
                "query_by": "text_convert",
            }
        )
        search_parameters_news.update(
            {
                "filter_by": f"last_update:<={end_bin_date_timestamp} && last_update:>={begin_bin_date_timestamp}",
                "query_by": "title_convert,keyword_convert",
            }
        )
        thread_news = ThreadWithReturnValue(
            target=client.collections["news"].documents.search,
            args=(search_parameters_news,),
        )
        thread_news.start()
        thread_fb_post = ThreadWithReturnValue(
            target=client.collections["fb_post"].documents.search,
            args=(search_parameters_fb_post,),
        )
        thread_fb_post.start()
        thread_fb_comment = ThreadWithReturnValue(
            target=client.collections["fb_comment"].documents.search,
            args=(search_parameters_fb_comment,),
        )
        thread_fb_comment.start()
        query_return_news = thread_news.join()
        query_return_fb_post = thread_fb_post.join()
        query_return_fb_comment = thread_fb_comment.join()
        count_analyst = {k: 0 for k in ["neutral", "positive", "negative"]}
        for i in query_return_fb_comment.get("hits", []):
            if i["document"]["sentiment"] in count_analyst.keys():
                count_analyst[i["document"]["sentiment"]] += 1
        result["response"].append(
            {
                "end_date": end_bin_date_timestamp,
                "begin_date": begin_bin_date_timestamp,
                "fb_post": query_return_fb_post.get("found", 0),
                "fb_comment": query_return_fb_comment.get("found", 0),
                "news": query_return_news.get("found", 0),
                "sentiment_analyst": count_analyst,
            }
        )
        end_bin_date_timestamp = begin_bin_date_timestamp
        begin_bin_date_timestamp = int(
            (
                datetime.fromtimestamp(begin_bin_date_timestamp)
                - timedelta(hours=time_frame_hour)
            ).timestamp()
        )
    return result
