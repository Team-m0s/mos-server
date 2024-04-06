from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models import Report, User, Post, Comment
from google.cloud import firestore

from domain.report.report_schema import PostReport, CommentReport, UserReport, AccompanyChatReport, PersonalChatReport
from domain.user import user_crud


def post_report(db: Session, reporter: User, post_report_create: PostReport):
    post = db.query(Post).filter(Post.id == post_report_create.post_id).first()
    db_report = Report(reporter_id=reporter.id,
                       report_reason_enum=post_report_create.report_reason,
                       report_reason_string=post_report_create.other,
                       report_date=datetime.now(),
                       post_id=post_report_create.post_id)
    db.add(db_report)

    post.report_count += 1

    if post.report_count >= 5:
        post.is_blinded = True
        post.blind_date = datetime.now()

    db.commit()


def comment_report(db: Session, reporter: User, comment_report_create: CommentReport):
    comment = db.query(Comment).filter(Comment.id == comment_report_create.comment_id).first()
    db_report = Report(reporter_id=reporter.id,
                       report_reason_enum=comment_report_create.report_reason,
                       report_reason_string=comment_report_create.other,
                       report_date=datetime.now(),
                       post_id=comment_report_create.post_id)
    db.add(db_report)

    comment.report_count += 1

    if comment.report_count >= 5:
        comment.is_blinded = True
        comment.blind_date = datetime.now()

    db.commit()


def accompany_chat_report(reporter: User, chat_report_create: AccompanyChatReport):
    chat_room_ref = user_crud.firebase_db.collection('chats').document(str(chat_report_create.accompany_id))
    message_ref = chat_room_ref.collection('messages').document(chat_report_create.message_id)

    message = message_ref.get()
    if message.exists:
        message_ref.update({'reportCount': firestore.Increment(1)})
        updated_message = message_ref.get()
        if updated_message.to_dict()['reportCount'] >= 5:
            message_ref.update({'isBlinded': True})
    else:
        raise ValueError("Chat not found")

    # Create a new collection 'reports' and add a document with id as combination of reporter's firebase_uuid and chat_id
    report_ref = user_crud.firebase_db.collection('reports') \
        .document(f"{reporter.firebase_uuid}_{chat_report_create.message_id}")

    # Store reporter's firebase_uuid, chat_id and report time in the document
    report_content = {
        "reporterUid": reporter.firebase_uuid,
        "chatId": chat_report_create.message_id,
        "reportReasonEnum": chat_report_create.report_reason,
        "reportReasonStr": chat_report_create.other
    }

    report_ref.set(report_content, merge=True)


def personal_chat_report(reporter: User, talk_report_create: PersonalChatReport):
    talk_ref = user_crud.firebase_db.collection('talks').document(talk_report_create.talk_id)
    message_ref = talk_ref.collection('messages').document(talk_report_create.message_id)

    message = message_ref.get()
    if message.exists:
        message_ref.update({'reportCount': firestore.Increment(1), 'isBlinded': True})
    else:
        raise ValueError("Chat not found")

    report_ref = user_crud.firebase_db.collection('reports') \
        .document(f"{reporter.firebase_uuid}_{talk_report_create.message_id}")

    report_content = {
        "reporterUid": reporter.firebase_uuid,
        "chatId": talk_report_create.message_id,
        "reportReasonEnum": talk_report_create.report_reason,
        "reportReasonStr": talk_report_create.other
    }

    report_ref.set(report_content, merge=True)


def user_report(db: Session, reporter: User, user_report_create: UserReport):
    user = db.query(User).filter(User.id == user_report_create.reported_user_id).first()
    db_report = Report(reporter_id=reporter.id,
                       report_reason_enum=user_report_create.report_reason,
                       report_reason_string=user_report_create.other,
                       report_date=datetime.now(),
                       reported_user_id=user_report_create.reported_user_id)
    db.add(db_report)

    user.report_count += 1

    if 15 <= user.report_count < 30:
        user.suspension_period = datetime.now() + timedelta(days=3)
    elif 30 <= user.report_count < 60:
        user.suspension_period = datetime.now() + timedelta(days=7)
    elif 60 <= user.report_count < 100:
        user.suspension_period = datetime.now() + timedelta(days=30)
    elif user.report_count >= 100:
        user.suspension_period = datetime.now() + timedelta(days=30000)

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
