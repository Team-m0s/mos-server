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
        bookmark.post = post

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
