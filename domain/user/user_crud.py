import math
from datetime import datetime, timedelta

import firebase_admin
import random
from sqlalchemy.orm import Session

from domain.accompany import accompany_crud
from models import User, Image, accompany_member, Accompany, UserActivity, NotificationSetting
from fastapi import FastAPI, Request, HTTPException, status
from jose import jwt
from jwt_token import ALGORITHM, SECRET_KEY
from jose.exceptions import JWTError, ExpiredSignatureError
from domain.user.user_schema import AuthSchema, UserUpdate, LanguagePref, NotificationSettingUpdate
from utils import file_utils
from firebase_admin import auth, firestore, credentials

# Check if the default app already exists
if not firebase_admin._apps:
    cred = credentials.Certificate("mos-app-a124a-firebase-adminsdk-xpjdc-71d6ca1659.json")
    firebase_admin.initialize_app(cred)

firebase_db = firestore.client()


def add_user_to_firestore(uid: str, user_info: dict, auth_schema: AuthSchema):
    user_data = {
        'firebase_uuid': uid,
        'nickName': auth_schema.nick_name,
        'profile_img': user_info.get("picture", None),
        'introduce': None,
        'lang_level': None
    }

    users_collection = firebase_db.collection('users')
    users_collection.document(uid).set(user_data)


def create_user_kakao(db: Session, user_info: dict, auth_schema: AuthSchema):
    firebase_user = auth.create_user(
        email=user_info['email'],
        email_verified=True,
        display_name=auth_schema.nick_name
    )

    add_user_to_firestore(uid=firebase_user.uid, user_info=user_info, auth_schema=auth_schema)

    unique_uuid = generate_unique_uuid(db)

    db_user = User(
        uuid=user_info['sub'],
        user_code=unique_uuid,
        firebase_uuid=firebase_user.uid,
        fcm_token=auth_schema.fcm_token,
        email=user_info['email'],
        nickName=auth_schema.nick_name,
        profile_img=user_info.get("picture", None),
        language_preference=auth_schema.language_preference,
        provider=auth_schema.provider,
        register_date=datetime.now()
    )
    db.add(db_user)
    db.commit()

    notification_setting = NotificationSetting(user_id=db_user.id,
                                               noti_activity=auth_schema.noti_activity,
                                               noti_chat=auth_schema.noti_chat,
                                               noti_marketing=auth_schema.noti_marketing)
    db.add(notification_setting)
    db.commit()

    return db_user


def create_test_user_kakao(db: Session, user_info: dict):
    db_user = User(
        uuid=user_info['email'],
        user_code='1111',
        firebase_uuid=user_info['email'],
        fcm_token='',
        email=user_info['email'],
        nickName=user_info['display_name'],
        profile_img=user_info.get("picture", None),
        provider='kakao',
        register_date=datetime.now()
    )
    db.add(db_user)
    db.commit()


def create_user_google(db: Session, user_info: dict, auth_schema: AuthSchema):
    firebase_user = auth.create_user(
        email=user_info['email'],
        email_verified=True,
        display_name=auth_schema.nick_name
    )

    add_user_to_firestore(uid=firebase_user.uid, user_info=user_info, auth_schema=auth_schema)

    unique_uuid = generate_unique_uuid(db)

    db_user = User(
        uuid=user_info['sub'],
        user_code=unique_uuid,
        firebase_uuid=firebase_user.uid,
        fcm_token=auth_schema.fcm_token,
        email=user_info['email'],
        nickName=auth_schema.nick_name,
        profile_img=user_info.get("picture", None),
        language_preference=auth_schema.language_preference,
        provider=auth_schema.provider,
        register_date=datetime.now()
    )
    db.add(db_user)
    db.commit()

    notification_setting = NotificationSetting(user_id=db_user.id,
                                               noti_activity=auth_schema.noti_activity,
                                               noti_chat=auth_schema.noti_chat,
                                               noti_marketing=auth_schema.noti_marketing)
    db.add(notification_setting)
    db.commit()

    return db_user


def create_user_apple(db: Session, user_info: dict, auth_schema: AuthSchema):
    firebase_user = auth.create_user(
        email=user_info['email'],
        email_verified=True,
        display_name=auth_schema.nick_name
    )

    add_user_to_firestore(uid=firebase_user.uid, user_info=user_info, auth_schema=auth_schema)

    unique_uuid = generate_unique_uuid(db)

    db_user = User(
        uuid=user_info['sub'],
        user_code=unique_uuid,
        firebase_uuid=firebase_user.uid,
        fcm_token=auth_schema.fcm_token,
        email=user_info['email'],
        nickName=auth_schema.nick_name,
        profile_img=user_info.get("picture", None),
        language_preference=auth_schema.language_preference,
        provider=auth_schema.provider,
        register_date=datetime.now()
    )
    db.add(db_user)
    db.commit()

    notification_setting = NotificationSetting(user_id=db_user.id,
                                               noti_activity=auth_schema.noti_activity,
                                               noti_chat=auth_schema.noti_chat,
                                               noti_marketing=auth_schema.noti_marketing)
    db.add(notification_setting)
    db.commit()

    return db_user


def delete_user_sso(db: Session, db_user: User):
    try:
        auth.delete_user(db_user.firebase_uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to delete user from Firebase: " + str(e))

    # Firestore에서 사용자 데이터 삭제
    try:
        firebase_db.collection('users').document(db_user.firebase_uuid).delete()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to delete user data from Firestore: " + str(e))

    db_user.nickName = '알수없음'
    db_user.uuid = ""
    db_user.firebase_uuid = ""
    db_user.fcm_token = ""
    db_user.provider = ""
    db_user.email = ""
    db_user.profile_img = ""
    db_user.introduce = ""
    db_user.point = 0
    db_user.language_preference = ""
    db_user.lang_level = None
    db_user.register_date = datetime(1970, 1, 1)
    db_user.report_count = 0
    db_user.last_nickname_change = None
    db_user.suspension_period = None

    leader_accompanies = db.query(Accompany).filter(Accompany.leader_id == db_user.id).all()

    for accompany in leader_accompanies:
        # Get the members of the accompany
        members = accompany_crud.get_members_by_accompany_id(db, accompany_id=accompany.id)

        # If the user is the only member, delete the accompany
        if len(members) == 1:
            accompany_crud.delete_accompany(db, accompany_id=accompany.id)
        else:
            # If there are other members, delegate the leader role to another member
            new_leader = next(member for member in members if member.id != db_user.id)
            accompany_crud.assign_new_leader(db, accompany=accompany, member=new_leader)

    # Get the accompanies where the user is a member
    member_accompanies = db.query(Accompany).join(accompany_member, Accompany.id == accompany_member.c.accompany_id) \
        .filter(accompany_member.c.user_id == db_user.id).all()

    # Remove the user from these accompanies
    for accompany in member_accompanies:
        accompany_crud.leave_accompany(db, accompany_id=accompany.id, member=db_user)

    db.query(NotificationSetting).filter(NotificationSetting.user_id == db_user.id).delete()

    db.commit()


def generate_unique_uuid(db: Session):
    while True:
        random_uuid = str(random.randint(1000000000, 9999999999))
        existing_user = db.query(User).filter(User.uuid == random_uuid).first()
        if not existing_user:
            return random_uuid


def update_fcm_token(db: Session, db_user: User, token: str):
    db_user.fcm_token = token
    db.commit()


def get_user_by_uuid(db: Session, uuid: str):
    return db.query(User).filter(User.uuid == uuid).first()


def get_user_by_firebase_uuid(db: Session, uuid: str):
    return db.query(User).filter(User.firebase_uuid == uuid).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_image_by_user_id(db: Session, user_id: int):
    return db.query(Image).filter(Image.user_id == user_id).first()


def get_image_by_hash(db: Session, image_hash: str):
    return db.query(Image).filter(Image.image_hash == image_hash).first()


def get_image_by_hash_all(db: Session, image_hash: str):
    return db.query(Image).filter(Image.image_hash == image_hash).all()


def get_user_notification_setting(db: Session, user: User):
    return db.query(NotificationSetting).filter(NotificationSetting.user_id == user.id).first()


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


def check_nickname_duplication(db: Session, nickname: str):
    db_user = db.query(User).filter(User.nickName == nickname).first()
    return db_user


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


def update_user_language_preference(db: Session, db_user: User, new_language_preference: LanguagePref):
    db_user.language_preference = new_language_preference.language_preference
    db.add(db_user)
    db.commit()


def update_user_notification_setting(db: Session, db_user: User, new_noti_setting: NotificationSettingUpdate):
    db_noti_setting = db.query(NotificationSetting).filter(NotificationSetting.user_id == db_user.id).first()

    if new_noti_setting.noti_activity is not None:
        db_noti_setting.noti_activity = new_noti_setting.noti_activity
    if new_noti_setting.noti_chat is not None:
        db_noti_setting.noti_chat = new_noti_setting.noti_chat
    if new_noti_setting.noti_marketing is not None:
        db_noti_setting.noti_marketing = new_noti_setting.noti_marketing

    db.commit()


def add_user_activity_and_points(db: Session, user: User, activity_type: str, activity_limit: int, activity_point: int):
    db_activity = UserActivity(user_id=user.id,
                               activity_type=activity_type,
                               activity_date=datetime.now())
    db.add(db_activity)
    db.commit()

    if activity_limit == 0:
        user.point += activity_point
    else:
        today = datetime.now().date()
        activity_today = db.query(UserActivity).filter(
            UserActivity.user_id == user.id,
            UserActivity.activity_type == activity_type,
            UserActivity.activity_date >= today).count()

        if activity_today <= activity_limit:
            user.point += activity_point
