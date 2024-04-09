from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from starlette import status
from typing import Optional, List
from datetime import datetime

from database import get_db
from firebase_admin import messaging
from domain.comment import comment_schema, comment_crud
from domain.post import post_crud
from domain.user import user_crud
from domain.like import like_crud
from domain.notice import notice_crud
from domain.accompany import accompany_crud

router = APIRouter(
    prefix="/api/comment",
)


@router.get("/detail/{comment_id}", response_model=List[comment_schema.Comment], tags=["Comment"])
def comment_detail(comment_id: int, token: Optional[str] = Header(None),
                   page: int = 0, size: int = 10, db: Session = Depends(get_db)):
    current_user = None
    _sub_comments = []
    total_pages, _sub_comments = comment_crud.get_sub_comments(db, comment_id=comment_id, start_index=page * size,
                                                               limit=size)
    if token:
        current_user = user_crud.get_current_user(db, token)

    for comment in _sub_comments:
        comment.total_pages = total_pages
        if current_user:
            comment_like = like_crud.get_comment_like(db, comment_id=comment.id, user=current_user)
            if comment_like:
                comment.is_liked_by_user = True

    return _sub_comments


@router.post("/create/post/{post_id}", response_model=comment_schema.Comment,
             status_code=status.HTTP_201_CREATED, tags=["Comment"])
def comment_create(post_id: int, _comment_create: comment_schema.CommentCreate, token: str = Header(),
                   db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    if current_user.suspension_period and current_user.suspension_period > datetime.now():
        raise HTTPException(status_code=403, detail="User is currently suspended")

    post = post_crud.get_post_by_post_id(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    created_comment = comment_crud.create_comment(db, post=post, comment_create=_comment_create, user=current_user)

    author = post_crud.get_post_author(db, post_id=post_id)

    message = messaging.Message(
        notification=messaging.Notification(
            title='댓글 알림',
            body='새로운 댓글이 달렸습니다.',
        ),
        data={
            "post_id": post.id
        },
        token=author.fcm_token
    )

    messaging.send(message)

    return created_comment


@router.post("/create/accompany/notice/{notice_id}", response_model=comment_schema.NoticeComment,
             status_code=status.HTTP_201_CREATED, tags=["Comment"])
def notice_comment_create(notice_id: int, _comment_create: comment_schema.NoticeCommentCreate, token: str = Header(),
                          db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    if current_user.suspension_period and current_user.suspension_period > datetime.now():
        raise HTTPException(status_code=403, detail="User is currently suspended")

    notice = notice_crud.get_notice_by_id(db, notice_id=notice_id)
    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"데이터를 찾을 수 없습니다.")

    accompany = accompany_crud.get_accompany_by_id(db, notice.accompany_id)
    # 멤버 목록 중 current_user의 id를 가진 멤버가 있는지 직접 확인
    if not any(member.id == current_user.id for member in accompany.member) and accompany.leader_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

    created_comment = comment_crud.create_notice_comment(db, notice=notice, notice_comment_create=_comment_create,
                                                         user=current_user)
    return created_comment


@router.post("/create/comment/{comment_id}", response_model=comment_schema.Comment,
             status_code=status.HTTP_201_CREATED, tags=["Comment"])
def sub_comment_create(comment_id: int, _comment_create: comment_schema.SubCommentCreate, token: str = Header(),
                       db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    if current_user.suspension_period and current_user.suspension_period > datetime.now():
        raise HTTPException(status_code=403, detail="User is currently suspended")

    comment = comment_crud.get_comment_by_id(db, comment_id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    elif comment.parent_id:
        raise HTTPException(status_code=404, detail="Can not create comment")

    created_comment = comment_crud.create_sub_comment(db, comment=comment, sub_comment_create=_comment_create,
                                                      user=current_user)
    return created_comment


@router.put("/update", response_model=comment_schema.Comment,
            status_code=status.HTTP_201_CREATED, tags=["Comment"])
def comment_update(_comment_update: comment_schema.CommentUpdate, token: str = Header(),
                   db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    if current_user.suspension_period and current_user.suspension_period > datetime.now():
        raise HTTPException(status_code=403, detail="User is currently suspended")

    comment = comment_crud.get_comment_by_id(db, comment_id=_comment_update.comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을수 없습니다.")
    if current_user != comment.user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

    sub_comments_count, updated_comment = comment_crud.update_comment(db, db_comment=comment,
                                                                      comment_update=_comment_update)
    updated_comment.sub_comments_count = sub_comments_count
    return updated_comment


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT, tags=["Comment"])
def comment_delete(_comment_delete: comment_schema.CommentDelete, token: str = Header(),
                   db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    comment = comment_crud.get_comment_by_id(db, _comment_delete.comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을수 없습니다.")
    if current_user != comment.user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="삭제 권한이 없습니다.")
    comment_crud.delete_comment(db, comment)
