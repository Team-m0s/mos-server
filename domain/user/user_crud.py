from sqlalchemy.orm import Session
from models import User
from fastapi import FastAPI, Request, HTTPException, status
import jwt_token
from jwt_token import ALGORITHM, SECRET_KEY
from jose.exceptions import JWTError

from domain.user.user_schema import UserCreate


def create_user(db: Session, user_info: dict):
    db_user = User(
        email=user_info['email'],
        nickName=user_info['display_name'],
        profile_img=user_info.get("picture", None)  # 'picture' 키가 없을 경우 None으로 처리
    )
    db.add(db_user)
    db.commit()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_current_user(db: Session, token: str):
    payload = jwt_token.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email: str = payload.get("sub")
    return db.query(User).filter(User.email == email).first()

