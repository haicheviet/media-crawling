from logging.config import dictConfig

from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware
from fastapi_admin.factory import app as admin_app
from tortoise.contrib.fastapi import register_tortoise

from app.api.api_demo.api import api_router
from app.core.config import settings
from app.logging_config import BASE_LOGGER
from app.filters import CustomFilter, LikeFilter

from tortoise.contrib.pydantic import pydantic_queryset_creator
from fastapi_admin.factory import app as admin_app
from fastapi_admin.depends import get_model

from fastapi_admin.site import Menu, Site
from fastapi_admin.schemas import BulkIn
from starlette.templating import Jinja2Templates

import logging

dictConfig(BASE_LOGGER)
TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {"models": {"models": ["app.models"], "default_connection": "default"}},
}
app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)
register_tortoise(app, config=TORTOISE_ORM, generate_schemas=True)
templates = Jinja2Templates(directory="app/templates")

app.mount('/admin', admin_app)

@admin_app.post("/rest/{resource}/bulk/test_bulk")
async def test_bulk(bulk_in: BulkIn, model=Depends(get_model)):
    qs = model.filter(pk__in=bulk_in.pk_list)
    pydantic = pydantic_queryset_creator(model)
    ret = await pydantic.from_queryset(qs)
    return ret.dict()


@admin_app.get("/home",)
async def home():
    return {"html": templates.get_template("home.html").render()}



@app.on_event("startup")
async def start_up():
    await admin_app.init(  # nosec
        admin_secret="test",
        permission=True,
        admin_log=True,
        site=Site(
            name="FastAPI-Admin DEMO",
            login_footer="FASweTAPI ADMIN - FastAPI Admin Dashboard",
            login_description="FastAPI Admin Dashboard",
            locale="en-US",
            locale_switcher=True,
            theme_switcher=True,
            menus=[
                Menu(name="Home", url="/", icon="fa fa-home"),
                Menu(
                    name="Content",
                    children=[
                        Menu(
                            name="Category",
                            url="/rest/Category",
                            icon="fa fa-list",
                            search_fields=("slug", LikeFilter),
                        ),
                        Menu(
                            name="Config",
                            url="/rest/Config",
                            icon="fa fa-gear",
                            import_=True,
                            search_fields=("key",),
                            custom_filters=[CustomFilter],
                        ),
                        Menu(
                            name="Product",
                            url="/rest/Product",
                            icon="fa fa-table",
                            search_fields=("name",),
                        ),
                    ],
                ),
                Menu(
                    name="External",
                    children=[
                        Menu(
                            name="Github",
                            url="https://github.com/long2ice/fastapi-admin",
                            icon="fa fa-github",
                            external=True,
                        ),
                    ],
                ),
                Menu(
                    name="Auth",
                    children=[
                        Menu(
                            name="UserAdmin",
                            url="/rest/User",
                            icon="fa fa-user",
                            search_fields=("username",),
                        ),
                        Menu(name="Role", url="/rest/Role", icon="fa fa-group",),
                        Menu(name="Permission", url="/rest/Permission", icon="fa fa-user-plus",),
                        Menu(
                            name="AdminLog",
                            url="/rest/AdminLog",
                            icon="fa fa-align-left",
                            search_fields=("action", "admin", "model"),
                        ),
                        Menu(name="Logout", url="/logout", icon="fa fa-lock",),
                    ],
                ),
            ],
        ),
    )

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
app.logger = logging.getLogger(__name__)
app.include_router(api_router, prefix=settings.API_V1_STR)
