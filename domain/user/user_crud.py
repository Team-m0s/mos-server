from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from models import User, Image
from fastapi import FastAPI, Request, HTTPException, status
from jose import jwt
from jwt_token import ALGORITHM, SECRET_KEY
from jose.exceptions import JWTError, ExpiredSignatureError
from domain.user.user_schema import AuthSchema, UserUpdate
from utils import file_utils


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


def get_image_by_user_id(db: Session, user_id: int):
    return db.query(Image).filter(Image.user_id == user_id).first()


def get_image_by_hash(db: Session, image_hash: str):
    return db.query(Image).filter(Image.image_hash == image_hash).first()


def get_image_by_hash_all(db: Session, image_hash: str):
    return db.query(Image).filter(Image.image_hash == image_hash).all()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_all_users(db: Session):
    return db.query(User).all()


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


def update_user_profile(db: Session, db_user: User, user_update: UserUpdate):
    if db_user.nickName != user_update.nickName:
        if db_user.last_nickname_change and datetime.now() - db_user.last_nickname_change < timedelta(days=30):
            raise HTTPException(status_code=400, detail="30일이 지나지 않아 닉네임을 변경할 수 없습니다.")

    db_user.nickName = user_update.nickName
    db_user.lang_level = user_update.lang_level
    db_user.introduce = user_update.introduce
    db_user.last_nickname_change = datetime.now()

    current_image = get_image_by_user_id(db, user_id=db_user.id)
    submitted_image = user_update.images_user

    # If a new image is submitted, and it's different from the current image
    if submitted_image and (not current_image or submitted_image.image_hash != current_image.image_hash):
        # 이미지가 다른 곳에서 사용중이면 저장소에서는 삭제 X
        other_images = get_image_by_hash_all(db, image_hash=submitted_image.image_hash)
        if any(image.user_id != db_user.id for image in other_images):
            db.delete(current_image)
            db.commit()
            current_image = None

        # Delete the current image
        if current_image:
            # Check if the image file deletion is successful
            try:
                file_utils.delete_image_file(current_image.image_url)
            except Exception as e:
                print(f"Failed to delete image file: {e}")
            else:
                db.delete(current_image)

        # Add the new image
        db_image = Image(image_url=submitted_image.image_url, image_hash=submitted_image.image_hash, user_id=db_user.id)
        db.add(db_image)

    if submitted_image is None:
        db_user.profile_img = None
    else:
        db_user.profile_img = f"https://www.mos-server.store/static/{submitted_image.image_url}"

    db.commit()
