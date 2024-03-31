from sqlalchemy.orm import Session
from models import Report, User, Post, Comment

from domain.report.report_schema import PostReport, CommentReport, UserReport


def post_report(db: Session, reporter: User, post_report_create: PostReport):
    post = db.query(Post).filter(Post.id == post_report_create.post_id).first()
    db_report = Report(reporter_id=reporter.id,
                       report_reason_enum=post_report_create.report_reason,
                       report_reason_string=post_report_create.other,
                       post_id=post_report_create.post_id)
    db.add(db_report)

    post.report_count += 1

    if post.report_count >= 5:
        post.is_blinded = True

    db.commit()


def comment_report(db: Session, reporter: User, comment_report_create: CommentReport):
    comment = db.query(Comment).filter(Comment.id == comment_report_create.comment_id).first()
    db_report = Report(reporter_id=reporter.id,
                       report_reason_enum=comment_report_create.report_reason,
                       report_reason_string=comment_report_create.other,
                       post_id=comment_report_create.post_id)
    db.add(db_report)

    comment.report_count += 1

    if comment.report_count >= 5:
        comment.is_blinded = True

    db.commit()


def user_report(db: Session, reporter: User, user_report_create: UserReport):
    user = db.query(User).filter(User.id == user_report_create.reported_user_id).first()
    db_report = Report(reporter_id=reporter.id,
                       report_reason_enum=user_report_create.report_reason,
                       report_reason_string=user_report_create.other,
                       reported_user_id=user_report_create.reported_user_id)
    db.add(db_report)

    user.report_count += 1
    db.commit()


def get_post_report(db: Session, user: User, post_id: int):
    db_report = db.query(Report).filter(Report.reporter_id == user.id, Report.post_id == post_id).first()
    return db_report


def get_comment_report(db: Session, user: User, comment_id: int):
    db_report = db.query(Report).filter(Report.reporter_id == user.id, Report.comment_id == comment_id).first()
    return db_report


def get_user_report(db: Session, reporter: User, user_id: int):
    db_report = db.query(Report).filter(Report.reporter_id == reporter.id, Report.reported_user_id == user_id).first()
    return db_report
