from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.comment import comment_schema, comment_crud
from domain.post import post_crud
from domain.user import user_crud
from domain.notice import notice_crud
from domain.accompany import accompany_crud

router = APIRouter(
    prefix="/api/comment",
)


@router.post("/create/post/{post_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Comment"])
def comment_create(token: str, post_id: int, _comment_create: comment_schema.CommentCreate,
                   db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    post = post_crud.get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comment_crud.create_comment(db, post=post, comment_create=_comment_create, user=current_user)


@router.post("/create/accompany/notice/{notice_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Comment"])
def notice_comment_create(token: str, notice_id: int, _comment_create: comment_schema.NoticeCommentCreate,
                          db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    notice = notice_crud.get_notice_by_id(db, notice_id=notice_id)
    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"데이터를 찾을 수 없습니다.")

    accompany = accompany_crud.get_accompany_by_id(db, notice.accompany_id)
    # 멤버 목록 중 current_user의 id를 가진 멤버가 있는지 직접 확인
    if not any(member.id == current_user.id for member in accompany.member):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

    comment_crud.create_notice_comment(db, notice=notice, notice_comment_create=_comment_create, user=current_user)


@router.post("/create/comment/{comment_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Comment"])
def sub_comment_create(token: str, comment_id: int, _comment_create: comment_schema.SubCommentCreate,
                       db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    comment = comment_crud.get_comment(db, comment_id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    elif comment.parent_id:
        raise HTTPException(status_code=404, detail="Can not create comment")
    comment_crud.create_sub_comment(db, comment=comment, sub_comment_create=_comment_create, user=current_user)


@router.put("/update", status_code=status.HTTP_204_NO_CONTENT, tags=["Comment"])
def comment_update(token: str, _comment_update: comment_schema.CommentUpdate,
                   db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    comment = comment_crud.get_comment(db, comment_id=_comment_update.comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을수 없습니다.")
    if current_user != comment.user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")
    comment_crud.update_comment(db, db_comment=comment, comment_update=_comment_update)


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT, tags=["Comment"])
def comment_delete(token: str, _comment_delete: comment_schema.CommentDelete,
                   db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    comment = comment_crud.get_comment(db, _comment_delete.comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을수 없습니다.")
    if current_user != comment.user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="삭제 권한이 없습니다.")
    comment_crud.delete_comment(db, comment)
