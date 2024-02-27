from sqlalchemy.orm import Session
from models import User
from fastapi import FastAPI, Request, HTTPException, status
import jwt
from jwt_token import ALGORITHM, SECRET_KEY
from jose.exceptions import JWTError


def create_user_kakao(db: Session, user_info: dict):
    db_user = User(
        email=user_info['email'],
        nickName=user_info['display_name'],
        profile_img=user_info.get("picture", None)  # 'picture' 키가 없을 경우 None으로 처리
    )
    db.add(db_user)
    db.commit()


def create_user_google(db: Session, user_info: dict):
    db_user = User(
        email=user_info['email'],
        nickName=user_info['name'],
        profile_img=user_info.get("picture", None)  # 'picture' 키가 없을 경우 None으로 처리
    )
    db.add(db_user)
    db.commit()


def create_user_apple(db: Session, user_info: dict):
    db_user = User(
        email=user_info['email'],
        nickName=user_info['name'],
        profile_img=user_info.get("picture", None)  # 'picture' 키가 없을 경우 None으로 처리
    )
    db.add(db_user)
    db.commit()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_current_user(db: Session, token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        print(user_email)
        if user_email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    else:
        user = get_user_by_email(db, user_email)
        if user is None:
            raise credentials_exception
        return user
