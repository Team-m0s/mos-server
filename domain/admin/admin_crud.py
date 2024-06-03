import json
import re
from datetime import datetime
from sqlalchemy.orm import Session
from models import User, Insight, Feedback
from domain.admin.admin_schema import InsightCreate, InsightUpdate
from models import InsightCategory


def get_all_users(db: Session):
    db_users = db.query(User).all()
    total_users = len(db_users)

    return total_users, db_users


def get_all_feedbacks(db: Session):
    db_feedbacks = db.query(Feedback).all()
    total_feedbacks = len(db_feedbacks)

    return total_feedbacks, db_feedbacks


def get_insights(db: Session, category: InsightCategory = None,
                 search_keyword_title: str = None, search_keyword_content: str = None,
                 search_keyword_title_exact: str = None, search_keyword_content_exact: str = None):
    query = db.query(Insight)

    if category:
        query = query.filter(Insight.category == category)

    if search_keyword_title:
        query = query.filter(Insight.title.contains(search_keyword_title))

    if search_keyword_content:
        query = query.filter(Insight.content.contains(search_keyword_content))

    if search_keyword_title_exact:
        regex = r'(^|\s){}(\s|$)'.format(re.escape(search_keyword_title_exact))
        query = query.filter(Insight.title.op('regexp')(regex))

    if search_keyword_content_exact:
        regex = r'(^|\s){}(\s|$)'.format(re.escape(search_keyword_content_exact))
        query = query.filter(Insight.content.op('regexp')(regex))

    query = query.order_by(Insight.create_date.desc())

    db_insights = query.all()
    total_insights = len(db_insights)

    return total_insights, db_insights


def get_insight_by_id(db: Session, insight_id: int):
    return db.query(Insight).filter(Insight.id == insight_id).first()


def create_insight(db: Session, insight_create: InsightCreate):
    title_json_data = json.dumps(insight_create.title, ensure_ascii=False)
    content_json_data = json.dumps(insight_create.content, ensure_ascii=False)
    db_insight = Insight(title=title_json_data,
                         content=content_json_data,
                         main_image=insight_create.main_image,
                         category=insight_create.category,
                         create_date=datetime.now())

    db.add(db_insight)
    db.commit()


def update_insight(db: Session, db_insight: Insight, insight_update: InsightUpdate):
    title_json_data = json.dumps(insight_update.title, ensure_ascii=False)
    content_json_data = json.dumps(insight_update.content, ensure_ascii=False)

    db_insight.title = title_json_data
    db_insight.content = content_json_data
    db_insight.create_date = datetime.now()

    db.add(db_insight)
    db.commit()
    db.refresh(db_insight)


def delete_insight(db: Session, db_insight: Insight):
    db.delete(db_insight)
    db.commit()
