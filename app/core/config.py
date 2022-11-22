import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, AnyUrl, BaseSettings, validator


class MysqlDsn(AnyUrl):
    allowed_schemes = {"mysql"}
    user_required = True


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # SERVER_NAME: str
    # SERVER_HOST: AnyHttpUrl
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str

    # MYSQL_SERVER: str
    # MYSQL_USER: str
    # MYSQL_PASSWORD: str
    # MYSQL_DB: str
    # SQLALCHEMY_DATABASE_URI: Optional[MysqlDsn] = None

    # @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    # def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
    #     if isinstance(v, str):
    #         return v
    #     return MysqlDsn.build(
    #         scheme="mysql",
    #         user=values.get("MYSQL_USER"),
    #         password=values.get("MYSQL_PASSWORD"),
    #         host=values.get("MYSQL_SERVER"),
    #         path=f"/{values.get('MYSQL_DB') or ''}",
    #     )

    FIRST_SUPERUSER: Any
    FIRST_SUPERUSER_PASSWORD: str
    # USERS_OPEN_REGISTRATION: bool = False

    # CELERY_RESULT_BACKEND: str = "rpc://guest:guest@queue:5672//"
    # CELERY_BROKER: str = "amqp://guest:guest@queue:5672//"
    TYPESENSE_KEY: str
    TYPESENSE_HOST: str
    TYPESENSE_PORT: str
    DATABASE_URL: str
    class Config:
        case_sensitive = True


settings = Settings()
