from datetime import datetime

from sqlalchemy.orm import Session
from models import User
from fastapi import FastAPI, Request, HTTPException, status
from jose import jwt
from jwt_token import ALGORITHM, SECRET_KEY
from jose.exceptions import JWTError, ExpiredSignatureError
from domain.user.user_schema import AuthSchema


def create_user_kakao(db: Session, user_info: dict, provider: AuthSchema):
    db_user = User(
        uuid=user_info['sub'],
        email=user_info['email'],
        nickName=user_info['nickname'],
        profile_img=user_info.get("picture", None),
        provider=provider.provider
    )
    db.add(db_user)
    db.commit()


def create_test_user_kakao(db: Session, user_info: dict):
    db_user = User(
        uuid=user_info['email'],
        email=user_info['email'],
        nickName=user_info['display_name'],
        profile_img=user_info.get("picture", None),
        provider='kakao'
    )
    db.add(db_user)
    db.commit()


def create_user_google(db: Session, user_info: dict, provider: AuthSchema):
    db_user = User(
        uuid=user_info['sub'],
        email=user_info['email'],
        nickName=user_info['name'],
        profile_img=user_info.get("picture", None),
        provider=provider.provider
    )
    db.add(db_user)
    db.commit()


def create_user_apple(db: Session, user_info: dict, name: str, provider: str):
    db_user = User(
        uuid=user_info['sub'],
        email=user_info['email'],
        nickName=name,
        profile_img=user_info.get("picture", None),
        provider=provider
    )
    db.add(db_user)
    db.commit()


def get_user_by_uuid(db: Session, uuid: str):
    return db.query(User).filter(User.uuid == uuid).first()


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
        user_uuid = payload.get("sub")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token format")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while verifying the token: " + str(e))
    else:
        user = get_user_by_uuid(db, user_uuid)
        if user is None:
            raise credentials_exception
        return user
