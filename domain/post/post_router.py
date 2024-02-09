from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from starlette import status

import jwt_token
from models import User
from database import get_db
from domain.post import post_schema, post_crud
from domain.user.user_crud import get_current_user

router = APIRouter(
    prefix="/api/post",
)


@router.get("/list", response_model=list[post_schema.Post], tags=["Post"])
def post_list(db: Session = Depends(get_db)):
    _post_list = post_crud.get_post_list(db)
    return _post_list


@router.get("/detail/{post_id}", response_model=post_schema.Post, tags=["Post"])
def post_detail(post_id: int, db: Session = Depends(get_db)):
    _post = post_crud.get_post(db, post_id=post_id)
    return _post


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT, tags=["Post"])
def post_create(token: str, _post_create: post_schema.PostCreate, db: Session = Depends(get_db)):
    current_user = get_current_user(db, token)
    _post_create = post_crud.create_post(db, post_create=_post_create, user=current_user)


@router.put("/update", status_code=status.HTTP_204_NO_CONTENT, tags=["Post"])
def post_update(token: str, _post_update: post_schema.PostUpdate, db: Session = Depends(get_db)):
    current_user = get_current_user(db, token)
    post = post_crud.get_post(db, post_id=_post_update.post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을수 없습니다.")
    if post.user != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")
    post_crud.update_post(db, db_post=post, post_update=_post_update)


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT, tags=["Post"])
def delete_post(token: str, _post_delete: post_schema.PostDelete, db: Session = Depends(get_db)):
    current_user = get_current_user(db, token)
    post = post_crud.get_post(db, post_id=_post_delete.post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을수 없습니다.")
    if post.user != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")
    post_crud.delete_post(db, db_post=post)
