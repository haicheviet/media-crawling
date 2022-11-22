from fastapi import APIRouter

from app.api.api_demo.endpoints import search_keyword, count_time_series, top_cloud
from app.api.deps import get_current_username

from fastapi import Depends


api_router = APIRouter()
# api_router.include_router(login.router, tags=["login"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
# api_router.include_router(items.router, prefix="/items", tags=["items"])
# api_router.include_router(fb_crawl.router, prefix="/fbPost", tags=["fb post"])
api_router.include_router(
    search_keyword.router,
    prefix="/search",
    tags=["fb post"],
    dependencies=[Depends(get_current_username)],
)
api_router.include_router(
    count_time_series.router,
    prefix="/count",
    tags=["count analyst"],
    dependencies=[Depends(get_current_username)],
)

api_router.include_router(
    top_cloud.router,
    prefix="/topCloud",
    tags=["topic cloud"],
    dependencies=[Depends(get_current_username)],
)

