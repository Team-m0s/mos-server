from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from starlette import status

import jwt_token
from models import User
from database import get_db
from domain.post import post_schema, post_crud
from domain.like import like_crud
from domain.user.user_crud import get_current_user
from domain.board import board_crud

router = APIRouter(
    prefix="/api/post",
)


@router.get("/list", response_model=post_schema.PostList, tags=["Post"],
            description="board_id가 0이면 전체 게시글 조회, page는 시작 index, size는 조회 개수입니다.")
def post_list(token: str = None, db: Session = Depends(get_db),
              board_id: int = 0, page: int = 0, size: int = 10, ):
    current_user = None
    if token:
        current_user = get_current_user(db, token)
    total, _post_list = post_crud.get_post_list(db, board_id=board_id, start_index=page * size, limit=size)

    if current_user:
        for post in _post_list:
            post_like = like_crud.get_post_like(db, post_id=post.id, user=current_user)
            if post_like:
                post.is_liked_by_user = True
            for comment in post.comment_posts:
                comment_like = like_crud.get_comment_like(db, comment_id=comment.id, user=current_user)
                if comment_like:
                    comment.is_liked_by_user = True

    return {
        'total': total,
        'post_list': _post_list,
    }


@router.get("/detail/{post_id}", response_model=post_schema.Post, tags=["Post"])
def post_detail(post_id: int, token: str = None, db: Session = Depends(get_db)):
    current_user = None
    _post = post_crud.get_post(db, post_id=post_id)

    if token:
        current_user = get_current_user(db, token)

    if current_user:
        post_like = like_crud.get_post_like(db, post_id=_post.id, user=current_user)
        if post_like:
            _post.is_liked_by_user = True

        for comment in _post.comment_posts:
            comment_like = like_crud.get_comment_like(db, comment_id=comment.id, user=current_user)
            if comment_like:
                comment.is_liked_by_user = True
    return _post


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT, tags=["Post"])
def post_create(token: str, board_id: int, _post_create: post_schema.PostCreate, db: Session = Depends(get_db)):
    current_user = get_current_user(db, token)
    board = board_crud.get_board(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    _post_create = post_crud.create_post(db, post_create=_post_create, board=board, user=current_user)


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
