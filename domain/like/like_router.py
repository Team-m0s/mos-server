from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.like import like_crud
from domain.post import post_crud
from domain.comment import comment_crud

router = APIRouter(
    prefix="/api/like",
)


# 유저 인증 과정 추가 필요
# 이미 좋아요 누른 게시글의 경우 다시 누르면 취소 기능 필요
@router.post("/post/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def like_post(post_id: int, db: Session = Depends(get_db)):
    post = post_crud.get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    like_crud.post_like(db, post=post)


@router.post("/comment/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def like_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = comment_crud.get_comment(db, comment_id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Post not found")
    like_crud.comment_like(db, comment=comment)

