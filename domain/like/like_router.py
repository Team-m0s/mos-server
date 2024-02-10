from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.like import like_crud
from domain.post import post_crud
from domain.comment import comment_crud
from domain.user import user_crud

router = APIRouter(
    prefix="/api/like",
)


# 유저 인증 과정 추가 필요
# 이미 좋아요 누른 게시글의 경우 다시 누르면 취소 기능 필요
@router.post("/post/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def like_post(token: str, post_id: int, db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    post = post_crud.get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    like = like_crud.get_like(db, post_id=post_id, user=current_user)
    if like:
        like_crud.minus_post_like(db, like=like, post=post)
        print("minus")
    else:
        like_crud.plus_post_like(db, post=post, user=current_user)
        print("plus")


@router.post("/comment/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def like_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = comment_crud.get_comment(db, comment_id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Post not found")
    like_crud.comment_like(db, comment=comment)

