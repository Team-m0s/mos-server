from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models import Report, User, Post, Comment, Accompany, Notice
from google.cloud import firestore

from domain.report.report_schema import PostReport, CommentReport, UserReport, AccompanyChatReport, \
    PersonalChatReport, AccompanyReport, NoticeReport
from domain.user import user_crud


def post_report(db: Session, reporter: User, post_report_create: PostReport):
    post = db.query(Post).filter(Post.id == post_report_create.post_id).first()
    db_report = Report(reporter_id=reporter.id,
                       report_reason_enum=[reason.value for reason in post_report_create.report_reason],
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
                       report_reason_enum=[reason.value for reason in comment_report_create.report_reason],
                       report_reason_string=comment_report_create.other,
                       report_date=datetime.now(),
                       comment_id=comment_report_create.comment_id)
    db.add(db_report)

    comment.report_count += 1

    if comment.report_count >= 5:
        comment.is_blinded = True
        comment.blind_date = datetime.now()

    db.commit()


def accompany_report(db: Session, reporter: User, accompany_report_create: AccompanyReport):
    accompany = db.query(Accompany).filter(Accompany.id == accompany_report_create.accompany_id).first()
    db_report = Report(reporter_id=reporter.id,
                       report_reason_enum=[reason.value for reason in accompany_report_create.report_reason],
                       report_reason_string=accompany_report_create.other,
                       report_date=datetime.now(),
                       accompany_id=accompany_report_create.accompany_id)
    db.add(db_report)

    accompany.report_count += 1

    if accompany.report_count >= 15:
        accompany.is_blinded = True
        accompany.blind_date = datetime.now()

    db.commit()


def accompany_notice_report(db: Session, reporter: User, notice_report_create: NoticeReport):
    notice = db.query(Notice).filter(Notice.id == notice_report_create.notice_id).first()
    db_report = Report(reporter_id=reporter.id,
                       report_reason_enum=[reason.value for reason in notice_report_create.report_reason],
                       report_reason_string=notice_report_create.other,
                       report_date=datetime.now(),
                       accompany_id=notice_report_create.accompany_id)
    db.add(db_report)

    notice.report_count += 1

    if notice.report_count >= 10:
        notice.is_blinded = True
        notice.blind_date = datetime.now()

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
        "reportReasonEnum": [reason.value for reason in chat_report_create.report_reason],
        "reportReasonStr": chat_report_create.other
    }

    report_ref.set(report_content, merge=True)


def personal_chat_report(reporter: User, talk_report_create: PersonalChatReport):
    talk_ref = user_crud.firebase_db.collection('talks').document(talk_report_create.talk_id)

    talk = talk_ref.get()
    if not talk.exists:
        raise ValueError("Chat not found")

    report_ref = user_crud.firebase_db.collection('reports') \
        .document(f"{reporter.firebase_uuid}_{talk_report_create.talk_id}")

    report_content = {
        "reporterUid": reporter.firebase_uuid,
        "chatId": talk_report_create.talk_id,
        "reportReasonEnum": [reason.value for reason in talk_report_create.report_reason],
        "reportReasonStr": talk_report_create.other
    }

    report_ref.set(report_content, merge=True)


def user_report(db: Session, reporter: User, user_report_create: UserReport):
    user = db.query(User).filter(User.id == user_report_create.reported_user_id).first()
    db_report = Report(reporter_id=reporter.id,
                       report_reason_enum=[reason.value for reason in user_report_create.report_reason],
                       report_reason_string=user_report_create.other,
                       report_date=datetime.now(),
                       reported_user_id=user_report_create.reported_user_id)
    db.add(db_report)

    user.report_count += 1

    if user.report_count % 10 == 0 and user.report_count < 40:
        user.suspension_period = datetime.now() + timedelta(days=3)
    elif user.report_count % 10 == 0 and 40 <= user.report_count < 70:
        user.suspension_period = datetime.now() + timedelta(days=7)
    elif (user.report_count - 70) % 15 == 0 and 70 <= user.report_count < 100:
        user.suspension_period = datetime.now() + timedelta(days=30)
    elif user.report_count >= 100:
        user.suspension_period = datetime.now() + timedelta(days=3650)

    db.commit()


def get_post_report(db: Session, user: User, post_id: int):
    db_report = db.query(Report).filter(Report.reporter_id == user.id, Report.post_id == post_id).first()
    return db_report


def get_comment_report(db: Session, user: User, comment_id: int):
    db_report = db.query(Report).filter(Report.reporter_id == user.id, Report.comment_id == comment_id).first()
    return db_report


def get_accompany_report(db: Session, user: User, accompany_id: int):
    db_report = db.query(Report).filter(Report.reporter_id == user.id, Report.accompany_id == accompany_id).first()
    return db_report


def get_notice_report(db: Session, user: User, notice_id: int):
    db_report = db.query(Report).filter(Report.reporter_id == user.id, Report.notice_id == notice_id).first()
    return db_report


def get_user_report(db: Session, reporter: User, user_id: int):
    db_report = db.query(Report).filter(Report.reporter_id == reporter.id, Report.reported_user_id == user_id).first()
    return db_report
