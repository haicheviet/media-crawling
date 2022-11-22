from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request

from app import crud, models, schemas
from app.api import deps
from app.core.decorator import decorator_logger_info

router = APIRouter()


@router.get("/", response_model=List[schemas.fb_post])
@decorator_logger_info
def read_fb_posts(
    request: Request,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve fb_posts.
    """
    if crud.user.is_superuser(current_user):
        fb_posts = crud.fb_post.get_multi(db, skip=skip, limit=limit)
    else:
        fb_posts = crud.fb_post.get_multi_by_owner(
            db=db, owner_id=current_user.id, skip=skip, limit=limit
        )
    return fb_posts


@router.post("/", response_model=schemas.fb_post)
@decorator_logger_info
def create_item(
    *,
    request: Request,
    db: Session = Depends(deps.get_db),
    item_in: schemas.ItemCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new fb_post.
    """
    fb_post = crud.fb_post.create_with_owner(
        db=db, obj_in=item_in, owner_id=current_user.id
    )
    return fb_post


@router.put("/{id}", response_model=schemas.fb_post)
@decorator_logger_info
def update_item(
    *,
    request: Request,
    db: Session = Depends(deps.get_db),
    id: int,
    item_in: schemas.ItemUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an fb_post.
    """
    fb_post = crud.fb_post.get(db=db, id=id)
    if not fb_post:
        raise HTTPException(status_code=404, detail="fb_post not found")
    if not crud.user.is_superuser(current_user) and (
        fb_post.owner_id != current_user.id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    fb_post = crud.fb_post.update(db=db, db_obj=fb_post, obj_in=item_in)
    return fb_post


@router.get("/{id}", response_model=schemas.fb_post)
@decorator_logger_info
def read_item(
    *,
    request: Request,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get fb_post by ID.
    """
    fb_post = crud.fb_post.get(db=db, id=id)
    if not fb_post:
        raise HTTPException(status_code=404, detail="fb_post not found")
    if not crud.user.is_superuser(current_user) and (
        fb_post.owner_id != current_user.id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return fb_post


@router.delete("/{id}", response_model=schemas.fb_post)
@decorator_logger_info
def delete_post(
    *,
    request: Request,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an fb_post.
    """
    fb_post = crud.fb_post.get(db=db, id=id)
    if not fb_post:
        raise HTTPException(status_code=404, detail="fb_post not found")
    if not crud.user.is_superuser(current_user) and (
        fb_post.owner_id != current_user.id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    fb_post = crud.fb_post.remove(db=db, id=id)
    return fb_post
