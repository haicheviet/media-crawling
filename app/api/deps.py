from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
# from app.db.session import SessionLocal
import secrets

from fastapi.security import HTTPBasicCredentials, HTTPBasic


security = HTTPBasic()
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


# def get_db() -> Generator:
#     try:
#         db = SessionLocal()
#         yield db
#     finally:
#         db.close()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    correct_username = secrets.compare_digest(
        credentials.username, settings.FIRST_SUPERUSER
    )
    correct_password = secrets.compare_digest(
        credentials.password, settings.FIRST_SUPERUSER_PASSWORD
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
