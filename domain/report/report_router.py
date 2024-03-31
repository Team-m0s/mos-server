from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db

from domain.user import user_crud
from domain.post import post_crud
from domain.comment import comment_crud
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


@router.post("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Report"])
def report_comment(report: report_schema.UserReport, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    user = user_crud.get_user_by_id(db, user_id=report.reported_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_report = report_crud.get_user_report(db, reporter=current_user, user_id=user.id)
    if existing_report:
        raise HTTPException(status_code=400, detail="You have already reported this user")

    report_crud.user_report(db, reporter=current_user, user_report_create=report)
