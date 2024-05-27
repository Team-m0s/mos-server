import json
from sqlalchemy.orm import Session
from models import User, Insight
from domain.admin.admin_schema import InsightCreate


def get_all_users(db: Session):
    db_users = db.query(User).all()
    total_users = len(db_users)

    return total_users, db_users


def get_insights(db: Session):
    return db.query(Insight).all()


def create_insight(db: Session, insight_create: InsightCreate):
    title_json_date = json.dumps(insight_create.title, ensure_ascii=False)
    content_json_data = json.dumps(insight_create.content, ensure_ascii=False)
    db_insight = Insight(title=title_json_date,
                         content=content_json_data)

    db.add(db_insight)
    db.commit()
