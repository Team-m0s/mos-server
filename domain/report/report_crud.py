from sqlalchemy.orm import Session
from models import Report, User, Post, Comment

from domain.report.report_schema import PostReport, CommentReport


def post_report(db: Session, reporter: User, post_report_create: PostReport):
    post = db.query(Post).filter(Post.id == post_report_create.post_id).first()
    db_report = Report(reporter_id=reporter.id,
                       report_reason_enum=post_report_create.report_reason,
                       report_reason_string=post_report_create.other,
                       post_id=post_report_create.post_id)
    db.add(db_report)

    post.report_count += 1
    db.commit()


def comment_report(db: Session, reporter: User, comment_report_create: CommentReport):
    comment = db.query(Comment).filter(Comment.id == comment_report_create.comment_id).first()
    db_report = Report(reporter_id=reporter.id,
                       report_reason_enum=comment_report_create.report_reason,
                       report_reason_string=comment_report_create.other,
                       post_id=comment_report_create.post_id)
    db.add(db_report)

    comment.report_count += 1
    db.commit()


def get_post_report(db: Session, user: User, post_id: int):
    db_report = db.query(Report).filter(Report.reporter_id == user.id, Report.post_id == post_id).first()
    return db_report


def get_comment_report(db: Session, user: User, comment_id: int):
    db_report = db.query(Report).filter(Report.reporter_id == user.id, Report.comment_id == comment_id).first()
    return db_report
