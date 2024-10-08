from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.accompany import accompany_schema
from domain.like import like_crud
from domain.post import post_schema
from domain.post import post_crud
from domain.user import user_crud
from domain.comment import comment_crud
from domain.bookmark import bookmark_crud
from domain.bookmark import bookmark_schema
from models import Comment

router = APIRouter(
    prefix="/api/bookmark",
)


@router.get("/list", response_model=list[bookmark_schema.Bookmark], tags=["Bookmark"])
def bookmark_list(token: str = Header(), db: Session = Depends(get_db), page: int = 0, size: int = 10):
    current_user = user_crud.get_current_user(db, token)
    total_pages, _my_bookmark_list = bookmark_crud.get_bookmark_list(db, user=current_user, start_index=page * size,
                                                                     limit=size)

    for bookmark in _my_bookmark_list:
        post = post_crud.get_post_by_post_id(db, post_id=bookmark.post_id)
        post.comment_count = comment_crud.get_post_comment_count(db, post_id=post.id)

        # 북마크 게시글 이미지 정보 설정
        images = post_crud.get_image_by_post_id(db, post_id=post.id)
        post.image_urls = [accompany_schema.ImageBase(id=image.id,
                                                      image_url=f"https://www.mos-server.store/static/{image.image_url}")
                           for
                           image in images if image.image_url] if images else []

        # 북마크 게시글 좋아요 여부 설정
        post_like = like_crud.get_post_like(db, post_id=post.id, user=current_user)
        if post_like:
            post.is_liked_by_user = True

        bookmark.post = post
        bookmark.post.total_pages = total_pages

    return _my_bookmark_list


@router.post("/post/{post_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Bookmark"])
def bookmark_post(post_id: int, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    post = post_crud.get_post_by_post_id(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    bookmark = bookmark_crud.get_post_bookmark(db, post_id=post_id, user=current_user)

    if bookmark:
        bookmark_crud.delete_bookmark(db, db_bookmark=bookmark)
    else:
        bookmark_crud.create_bookmark(db, post=post, user=current_user)
