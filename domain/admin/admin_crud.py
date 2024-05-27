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
    json_data = json.dumps(insight_create.content)
    db_insight = Insight(content=json_data)

    db.add(db_insight)
    db.commit()