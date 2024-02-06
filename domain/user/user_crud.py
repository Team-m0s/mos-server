from sqlalchemy.orm import Session
from models import User
from fastapi import FastAPI, Request, HTTPException, status

from domain.user.user_schema import UserCreate


def create_user(db: Session, user_info: dict, user_create: UserCreate):
    existing_user = get_user_by_email(db, user_info['email'])
    if existing_user:
        # 사용자가 이미 존재하면 추가 작업 없이 종료
        return existing_user

    # 신규 사용자일 경우, 사용자 정보를 데이터베이스에 저장
    db_user = User(
        email=user_info['email'],
        nickName=user_create.nickname,
        profile_img=user_info.get("picture", None)  # 'picture' 키가 없을 경우 None으로 처리
    )
    db.add(db_user)
    db.commit()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_current_user(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="로그인이 필요합니다.")
    return user
