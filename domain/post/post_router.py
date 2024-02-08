from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from starlette import status

import jwt_token
from database import get_db
from domain.post import post_schema, post_crud
router = APIRouter(
    prefix="/api/post",
)


@router.get("/list", response_model=list[post_schema.Post])
def post_list(db: Session = Depends(get_db)):
    _post_list = post_crud.get_post_list(db)
    return _post_list


@router.get("/detail/{post_id}", response_model=post_schema.Post)
def post_detail(post_id: int, db: Session = Depends(get_db)):
    _post = post_crud.get_post(db, post_id=post_id)
    return _post


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def post_create(_post_create: post_schema.PostCreate, db: Session = Depends(get_db)):
    _post_create = post_crud.create_post(db, post_create=_post_create)
