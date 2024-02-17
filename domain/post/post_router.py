from typing import Optional, List
from fastapi import APIRouter, Depends, Header, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
from starlette import status
from uuid import uuid4
from models import User
from database import get_db

from utils import file_utils
from domain.post import post_schema, post_crud
from domain.like import like_crud
from domain.user.user_crud import get_current_user
from domain.board import board_crud
from domain.accompany import accompany_schema

router = APIRouter(
    prefix="/api/post",
)


@router.get("/list", response_model=post_schema.PostList, tags=["Post"],
            description="board_id가 0이면 전체 게시글 조회, page는 시작 index, size는 조회 개수입니다. keyword를 사용해 검색 가능합니다."
                        "\n정렬 순서는 기본 최신순이며, 과거순은 'oldest' 좋아요순은 'popularity'를 넣어서 요청하시면 됩니다.")
def post_list(token: str = None, db: Session = Depends(get_db),
              board_id: int = 0, page: int = 0, size: int = 10, search_keyword: str = None, sort_order: str = 'latest'):
    current_user = None
    if token:
        current_user = get_current_user(db, token)
    total, _post_list = post_crud.get_post_list(db, board_id=board_id, start_index=page * size, limit=size,
                                                search_keyword=search_keyword, sort_order=sort_order)

    for post in _post_list:
        images = post_crud.get_image_by_post_id(db, post_id=post.id)
        post.image_urls = [accompany_schema.ImageBase(id=image.id,
                           image_url=f"http://127.0.0.1:8000/static/{image.image_url}") for
                           image in images if image.image_url] if images else []

    if current_user:
        for post in _post_list:
            post_like = like_crud.get_post_like(db, post_id=post.id, user=current_user)
            if post_like:
                post.is_liked_by_user = True

    return {
        'total': total,
        'post_list': _post_list,
    }


@router.get("/detail/{post_id}", response_model=post_schema.Post, tags=["Post"])
def post_detail(post_id: int, token: str = None, comment_sort_order: str = 'oldest', db: Session = Depends(get_db)):
    current_user = None
    _post = post_crud.get_post(db, post_id=post_id, comment_sort_order=comment_sort_order)

    if not _post:
        raise HTTPException(status_code=404, detail="Post not found")

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
def post_create(token: str = Form(...), board_id: int = Form(...),
                subject: str = Form(...), content: str = Form(...),
                is_anonymous: bool = Form(...),
                images: List[UploadFile] = File(None),
                db: Session = Depends(get_db)):
    current_user = get_current_user(db, token)
    board = board_crud.get_board(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    image_creates = []
    if images:
        for image in images:
            image_hash = file_utils.calculate_image_hash(image)
            existing_image = post_crud.get_image_by_hash(db, image_hash)
            if existing_image:
                image_creates.append(accompany_schema.ImageCreate(image_url=existing_image.image_url, image_hash=image_hash))
            else:
                image_path = file_utils.save_image_file(image)
                image_creates.append(accompany_schema.ImageCreate(image_url=image_path, image_hash=image_hash))

    post_create_data = post_schema.PostCreate(subject=subject, content=content,
                                              is_anonymous=is_anonymous, images_post=image_creates)

    post_crud.create_post(db, post_create=post_create_data, board=board, user=current_user)


@router.put("/update", status_code=status.HTTP_204_NO_CONTENT, tags=["Post"])
def post_update(token: str = Form(...), post_id: int = Form(...),
                subject: str = Form(...), content: str = Form(...),
                is_anonymous: bool = Form(...),
                images: List[UploadFile] = File(None),
                db: Session = Depends(get_db)):
    current_user = get_current_user(db, token)
    post = post_crud.get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을수 없습니다.")
    if post.user != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

    image_creates = []
    if images:
        for image in images:
            image_hash = file_utils.calculate_image_hash(image)
            existing_image = post_crud.get_image_by_hash(db, image_hash)
            # 기존에 저장된 이미지와 hash 비교, 이미 존재하는 이미지면 다시 저장 X
            if existing_image:
                image_creates.append(accompany_schema.ImageCreate(image_url=existing_image.image_url, image_hash=image_hash))
            else:
                image_path = file_utils.save_image_file(image)
                image_creates.append(accompany_schema.ImageCreate(image_url=image_path, image_hash=image_hash))

    post_update_data = post_schema.PostUpdate(subject=subject, content=content,
                                              is_anonymous=is_anonymous, images_post=image_creates, post_id=post_id)

    post_crud.update_post(db, db_post=post, post_update=post_update_data)


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
