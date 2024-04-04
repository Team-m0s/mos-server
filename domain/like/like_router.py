from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from starlette import status
from datetime import datetime

from database import get_db
from domain.like import like_crud
from domain.post import post_crud
from domain.comment import comment_crud
from domain.user import user_crud
from domain.accompany import accompany_crud

router = APIRouter(
    prefix="/api/like",
)


@router.post("/post/{post_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Like"])
def like_post(post_id: int, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    if current_user.suspension_period and current_user.suspension_period > datetime.now():
        raise HTTPException(status_code=403, detail="User is currently suspended")

    post = post_crud.get_post_by_post_id(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    like = like_crud.get_post_like(db, post_id=post_id, user=current_user)
    if like:
        like_crud.minus_post_like(db, like=like, post=post)
    else:
        like_crud.plus_post_like(db, post=post, user=current_user)


@router.post("/comment/{comment_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Like"])
def like_comment(comment_id: int, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    if current_user.suspension_period and current_user.suspension_period > datetime.now():
        raise HTTPException(status_code=403, detail="User is currently suspended")

    comment = comment_crud.get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    like = like_crud.get_comment_like(db, comment_id=comment_id, user=current_user)
    if like:
        like_crud.minus_comment_like(db, like=like, comment=comment)
    else:
        like_crud.plus_comment_like(db, comment=comment, user=current_user)


@router.post("/accompany/{accompany_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Like"])
def like_accompany(accompany_id: int, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    if current_user.suspension_period and current_user.suspension_period > datetime.now():
        raise HTTPException(status_code=403, detail="User is currently suspended")

    accompany = accompany_crud.get_accompany_by_id(db, accompany_id=accompany_id)
    if not accompany:
        raise HTTPException(status_code=404, detail="Accompany not found")
    like = like_crud.get_accompany_like(db, accompany_id=accompany_id, user=current_user)
    if like:
        like_crud.minus_accompany_like(db, like=like, accompany=accompany)
    else:
        like_crud.plus_accompany_like(db, accompany=accompany, user=current_user)

