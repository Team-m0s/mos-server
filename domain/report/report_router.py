from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db

from domain.user import user_crud
from domain.post import post_crud
from domain.comment import comment_crud
from domain.accompany import accompany_crud
from domain.notice import notice_crud
from domain.vocabulary import vocabulary_crud
from domain.report import report_schema
from domain.report import report_crud

router = APIRouter(
    prefix="/api/report",
)


@router.post("/post/{post_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Report"])
def report_post(report: report_schema.PostReport, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    post = post_crud.get_post_by_post_id(db, post_id=report.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing_report = report_crud.get_post_report(db, user=current_user, post_id=post.id)
    if existing_report:
        raise HTTPException(status_code=400, detail="You have already reported this post")

    report_crud.post_report(db, reporter=current_user, post_report_create=report)


@router.post("/comment/{comment_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Report"])
def report_comment(report: report_schema.CommentReport, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    comment = comment_crud.get_comment_by_id(db, comment_id=report.comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    existing_report = report_crud.get_comment_report(db, user=current_user, comment_id=comment.id)
    if existing_report:
        raise HTTPException(status_code=400, detail="You have already reported this comment")

    report_crud.comment_report(db, reporter=current_user, comment_report_create=report)


@router.post("/accompany/{accompany_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Report"])
def report_accompany(report: report_schema.AccompanyReport, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    accompany = accompany_crud.get_accompany_by_id(db, accompany_id=report.accompany_id)
    if not accompany:
        raise HTTPException(status_code=404, detail="Accompany not found")

    existing_report = report_crud.get_accompany_report(db, user=current_user, accompany_id=accompany.id)
    if existing_report:
        raise HTTPException(status_code=400, detail="You have already reported this accompany")

    report_crud.accompany_report(db, reporter=current_user, accompany_report_create=report)


@router.post("/accompany/notice/{notice_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Report"])
def report_accompany_notice(report: report_schema.NoticeReport, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    notice = notice_crud.get_notice_by_id(db, notice_id=report.notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")

    existing_report = report_crud.get_notice_report(db, user=current_user, notice_id=notice.id)
    if existing_report:
        raise HTTPException(status_code=400, detail="You have already reported this notice")

    report_crud.accompany_notice_report(db, reporter=current_user, notice_report_create=report)


@router.post("/vocabulary/{vocabulary_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Report"])
def report_vocabulary(report: report_schema.VocabularyReport, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    vocabulary = vocabulary_crud.get_vocabulary_by_id(db, vocabulary_id=report.vocabulary_id)
    if not vocabulary:
        raise HTTPException(status_code=404, detail="Vocabulary not found")

    existing_report = report_crud.get_vocabulary_report(db, user=current_user, vocabulary_id=vocabulary.id)
    if existing_report:
        raise HTTPException(status_code=400, detail="You have already reported this vocabulary")

    report_crud.vocabulary_report(db, reporter=current_user, voca_report_create=report)


@router.post("/accompany/chat", status_code=status.HTTP_204_NO_CONTENT, tags=["Report"])
def report_accompany_chat(report: report_schema.AccompanyChatReport, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    # Create a reference to the report document
    report_id = f"{current_user.firebase_uuid}_{report.message_id}"
    report_ref = user_crud.firebase_db.collection('reports').document(report_id)

    # Check if the report already exists
    if report_ref.get().exists:
        raise HTTPException(status_code=400, detail="You have already reported this chat")

    report_crud.accompany_chat_report(reporter=current_user, chat_report_create=report)


@router.post("/personal/chat", status_code=status.HTTP_204_NO_CONTENT, tags=["Report"])
def report_personal_chat(report: report_schema.PersonalChatReport, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    report_id = f"{current_user.firebase_uuid}_{report.talk_id}"
    report_ref = user_crud.firebase_db.collection('reports').document(report_id)

    if report_ref.get().exists:
        raise HTTPException(status_code=400, detail="You have already reported this chat")

    report_crud.personal_chat_report(db, reporter=current_user, talk_report_create=report)


@router.post("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Report"])
def report_user(report: report_schema.UserReport, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    user = user_crud.get_user_by_id(db, user_id=report.reported_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_report = report_crud.get_user_report(db, reporter=current_user, user_id=user.id)
    if existing_report:
        raise HTTPException(status_code=400, detail="You have already reported this user")

    report_crud.user_report(db, reporter=current_user, user_report_create=report)


@router.post("/feedback", status_code=status.HTTP_204_NO_CONTENT, tags=["Report"])
def send_feedback(feedback: report_schema.UserFeedback, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    report_crud.user_feedback(db, reporter=current_user, user_feedback_create=feedback)
