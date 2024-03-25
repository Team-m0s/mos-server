from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from database import get_db

from domain.user import user_crud
from domain.post import post_crud
from domain.comment import comment_crud
from domain.report import report_schema
from domain.report import report_crud

router = APIRouter(
    prefix="/api/post",
)


@router.post("/post/{post_id}")
def report_post(report: report_schema.PostReport, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    post = post_crud.get_post_by_post_id(db, post_id=report.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    report_crud.post_report(db, reporter=current_user, post_report_create=report)


@router.post("/comment/{comment_id}")
def report_post(report: report_schema.CommentReport, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    comment = comment_crud.get_comment_by_id(db, comment_id=report.comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    report_crud.comment_report(db, reporter=current_user, comment_report_create=report)