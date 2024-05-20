from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from starlette import status
from typing import Optional, List
from datetime import datetime

from database import get_db
from firebase_admin import messaging
from domain.comment import comment_schema, comment_crud
from domain.post.post_schema import PostDetail
from domain.post import post_crud
from domain.user import user_crud
from domain.like import like_crud
from domain.notice import notice_crud
from domain.vocabulary import vocabulary_crud
from domain.notification import notification_crud
from domain.accompany import accompany_crud
from domain.block import block_crud

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


@router.get("/best", response_model=List[comment_schema.Comment], tags=["Comment"])
def get_best_comments(page: int = 0, size: int = 10, db: Session = Depends(get_db)):
    total_pages, best_comments = comment_crud.get_best_comments(db, start_index=page * size, limit=size)
    for comment in best_comments:
        comment.total_pages = total_pages
    return best_comments


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

    author = post.user
    badge_count = notification_crud.get_unread_notification_count(db, user=author)

    blocked_users = block_crud.get_blocked_list(db, user=author)
    if current_user.uuid not in [block.blocked_uuid for block in blocked_users]:
        if author.uuid != current_user.uuid:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=f'내 게시글 "{post.subject}"에 새로운 답글이 달렸어요.',
                    body=_comment_create.content,
                ),
                data={
                    "post_id": str(post.id)
                },
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            #badge=badge_count,
                            sound='default',
                            content_available=True
                        )
                    )
                ),
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


@router.post("/create/vocabulary/{vocabulary_id}", response_model=comment_schema.VocabularyComment,
             status_code=status.HTTP_201_CREATED, tags=["Comment"])
def voca_comment_create(vocabulary_id: int, _comment_create: comment_schema.VocaCommentCreate, token: str = Header(),
                        db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    if current_user.suspension_period and current_user.suspension_period > datetime.now():
        raise HTTPException(status_code=403, detail="User is currently suspended")

    vocabulary = vocabulary_crud.get_vocabulary_by_id(db, vocabulary_id=vocabulary_id)
    if not vocabulary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vocabulary not found")
    elif vocabulary.is_solved:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vocabulary is closed")

    # Check if the user has already commented on the vocabulary
    existing_comment = comment_crud.get_vocabulary_comment(db, user_id=current_user.id, vocabulary_id=vocabulary_id)
    if existing_comment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User has already commented on this "
                                                                            "vocabulary")

    created_comment = comment_crud.create_vocabulary_comment(db, vocabulary=vocabulary,
                                                             voca_comment_create=_comment_create, user=current_user)

    author = vocabulary.author
    badge_count = notification_crud.get_unread_notification_count(db, user=author)

    blocked_users = block_crud.get_blocked_list(db, user=author)
    if current_user.uuid not in [block.blocked_uuid for block in blocked_users]:
        if author.uuid != current_user.uuid:
            message = messaging.Message(
                notification=messaging.Notification(
                    title='📗 내 단어장에 새로운 답변이 달렸어요!',
                    body=_comment_create.content,
                ),
                data={
                    "vocabulary_id": str(vocabulary.id)
                },
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            #badge=badge_count,
                            sound='default',
                            content_available=True
                        )
                    )
                ),
                token=author.fcm_token
            )

            messaging.send(message)

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

    author = comment.user
    badge_count = notification_crud.get_unread_notification_count(db, user=author)

    blocked_users = block_crud.get_blocked_list(db, user=author)
    if current_user.uuid not in [block.blocked_uuid for block in blocked_users]:
        if author.uuid != current_user.uuid:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=f'내 댓글 "{comment.content}"에 새로운 답글이 달렸어요.',
                    body=_comment_create.content,
                ),
                data={
                    "post_id": str(comment.post_id)
                },
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            #badge=badge_count,
                            sound='default',
                            content_available=True
                        )
                    )
                ),
                token=author.fcm_token
            )

            messaging.send(message)

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
