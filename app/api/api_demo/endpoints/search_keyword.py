from typing import Any, List
from app.core.decorator import decorator_logger_info
from app.utils import convert_accented_vietnamese_text
from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from enum import Enum
from pydantic import BaseModel
from app.db.init_typesense import client

router = APIRouter()


class ResponseSearchKeyword(BaseModel):
    hits: List[Any]
    found: int


class SourceCrawl(str, Enum):
    fb_comment = "fb_comment"
    fb_post = "fb_post"
    fb_all = "fb_all"


def mapping_mark_text(text_convert, text_raw):
    list_text_raw = text_raw.split()
    for index, i in enumerate(text_convert.split()):
        if "<mark>" in i and "</mark>" in i:
            list_text_raw[index] = "<mark>" + list_text_raw[index] + "</mark>"
    list_text_raw = " ".join(list_text_raw)
    return list_text_raw


@router.get("/searchKeywordNews", response_model=ResponseSearchKeyword)
@decorator_logger_info
def search_keyword_news(
    request: Request,
    keyword: str,
    begin_date_timestamp: int = 0,
    end_date_timestamp: int = 0,
    limit: int = 10,
    page: int = 1,
):
    keyword = convert_accented_vietnamese_text(keyword)
    search_parameters = {
        "q": keyword,
        "query_by": "title_convert,keyword_convert",
        # "sort_by": "last_update:desc",
        "page": page,
        "num_typos": 1,
        "per_page": limit,
    }
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
    if end_date_timestamp:
        search_parameters.update({"filter_by": f"last_update:<={end_date_timestamp}"})

    query_return = client.collections["news"].documents.search(search_parameters)

    result = {}
    if query_return:
        result["hits"] = query_return.get("hits")
        result["found"] = query_return.get("found")
        for i in result["hits"]:
            temp_highlights = []
            for j in i["highlights"]:
                temp_match = j.copy()
                temp_match["field"] = j["field"].replace("_convert", "")
                text_convert = j["snippet"]
                text_raw = i["document"][temp_match["field"]]
                temp_match["snippet"] = mapping_mark_text(
                    text_convert=text_convert, text_raw=text_raw
                )
                temp_highlights.append(temp_match)

            i["highlights"] = temp_highlights
    if not result:
        raise HTTPException(status_code=404, detail="Keyword mention not found")
    return result


@router.get("/searchKeywordFb", response_model=ResponseSearchKeyword)
@decorator_logger_info
def search_keyword_fb(
    request: Request,
    keyword: str,
    begin_date_timestamp: int = 0,
    end_date_timestamp: int = 0,
    source_crawl_fb: SourceCrawl = SourceCrawl.fb_all,
    limit: int = 10,
    page: int = 1
    ):
    keyword = convert_accented_vietnamese_text(keyword)
    search_parameters = {
        "q": keyword,
        "page": page,
        "num_typos": 1,
        "per_page": limit,
    }
    if source_crawl_fb == SourceCrawl.fb_comment:
        search_parameters.update({"query_by": "fb_comment_text_convert"})
    elif source_crawl_fb == SourceCrawl.fb_post:
        search_parameters.update({"query_by": "fb_post_text_convert"})
    else:
        search_parameters.update(
            {"query_by": "fb_comment_text_convert,fb_post_text_convert"}
        )
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
    if end_date_timestamp:
        search_parameters.update({"filter_by": f"last_update:<={end_date_timestamp}"})

    query_return = client.collections["fb_all"].documents.search(search_parameters)

    result = {}
    if query_return:
        result["hits"] = query_return.get("hits")
        result["found"] = query_return.get("found")
        for i in result["hits"]:
            temp_highlights = []
            for j in i["highlights"]:
                temp_match = j.copy()
                temp_match["field"] = j["field"].replace("_convert", "")
                text_convert = j["snippet"]
                text_raw = i["document"][temp_match["field"]]
                temp_match["snippet"] = mapping_mark_text(
                    text_convert=text_convert, text_raw=text_raw
                )
                temp_highlights.append(temp_match)

            i["highlights"] = temp_highlights
    if not result:
        raise HTTPException(status_code=404, detail="Keyword mention not found")
    return result
