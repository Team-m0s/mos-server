# auth.py
from datetime import datetime, timedelta
from fastapi import Request, Depends, HTTPException, Header, Body, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
import os
import jwt_token
from database import get_db
from domain.user import user_crud
from domain.user.user_schema import AuthSchema
from firebase_admin import auth
from fastapi_sso.sso.kakao import KakaoSSO

router = APIRouter()

sso = KakaoSSO(
    client_id=os.getenv("KAKAO_CLIENT_ID"),
    client_secret=os.getenv("KAKAO_CLIENT_SECRET"),
    redirect_uri="http://ec2-13-125-254-93.ap-northeast-2.compute.amazonaws.com:8000/login/kakao/callback",
    allow_insecure_http=True,
)

@router.get("/login/kakao", tags=["Test"])
async def kakao_login():
    """Initialize auth and redirect"""
    with sso:
        return await sso.get_login_redirect()


@router.get("/login/kakao/callback", tags=["Test"])
async def kakao_auth(request: Request, db: Session = Depends(get_db)):
    """Verify login"""
    with sso:
        user = await sso.verify_and_process(request, params={"client_secret": os.getenv("KAKAO_CLIENT_SECRET")})

    user_info = dict(user)
    db_user = user_crud.get_user_by_uuid(db, user_info['email'])

    if db_user is None:
        print("회원가입 성공")
        user_crud.create_test_user_kakao(db, user_info=user_info)

    # 토큰 생성
    access_token = jwt_token.create_access_token(data={"sub": user_info['email']}, expires_delta=timedelta(minutes=600))
    refresh_token = jwt_token.create_refresh_token(data={"sub": user_info['email']})

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/login/google/auth", tags=["Authentication"])
async def google_auth(auth_schema: AuthSchema = Body(...), token: str = Header(), db: Session = Depends(get_db)):
    try:
        # Try to verify the token with the first client ID
        id_info = id_token.verify_oauth2_token(token, requests.Request(), os.getenv("GOOGLE_CLIENT_ID_IOS"))
    except ValueError:
        try:
            # If the first verification fails, try with the second client ID
            id_info = id_token.verify_oauth2_token(token, requests.Request(), os.getenv("GOOGLE_CLIENT_ID"))
        except ValueError:
            # If both verifications fail, raise an exception
            raise HTTPException(status_code=400, detail="Invalid token.")

    user_info = dict(id_info)
    db_user = user_crud.get_user_by_uuid(db, user_info['sub'])

    if auth_schema.nick_name:
        if db_user is not None:
            if datetime.now() < db_user.deletion_date:
                raise HTTPException(status_code=400, detail="Cannot re-register within 7 days after deletion.")
        else:
            db_user = user_crud.create_user_kakao(db, user_info=user_info, auth_schema=auth_schema)

    else:
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if db_user.deletion_date is not None:
            raise HTTPException(status_code=404, detail="User not found")

        user_crud.update_fcm_token(db, db_user=db_user, token=auth_schema.fcm_token)

    access_token_expires = timedelta(minutes=15)  # 토큰 유효 시간 설정
    access_token = jwt_token.create_access_token(data={"sub": user_info['sub']},
                                                 expires_delta=access_token_expires)
    refresh_token = jwt_token.create_refresh_token(data={"sub": user_info['sub']})

    firebase_token = None
    if db_user:
        firebase_token = auth.create_custom_token(db_user.firebase_uuid)

    return {"access_token": access_token, "refresh_token": refresh_token, "firebase_token": firebase_token}


@router.post("/login/kakao/auth", tags=["Authentication"])
async def kakao_auth(auth_schema: AuthSchema = Body(...), token: str = Header(), db: Session = Depends(get_db)):
    id_info = await jwt_token.verify_kakao_token(token)

    user_info = dict(id_info)
    db_user = user_crud.get_user_by_uuid(db, user_info['sub'])

    if auth_schema.nick_name:
        if db_user is not None:
            if datetime.now() < db_user.deletion_date:
                raise HTTPException(status_code=400, detail="Cannot re-register within 7 days after deletion.")
        else:
            db_user = user_crud.create_user_kakao(db, user_info=user_info, auth_schema=auth_schema)

    else:
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if db_user.deletion_date is not None:
            raise HTTPException(status_code=404, detail="User not found")

        user_crud.update_fcm_token(db, db_user=db_user, token=auth_schema.fcm_token)

    # 토큰 생성
    access_token = jwt_token.create_access_token(data={"sub": user_info['sub']}, expires_delta=timedelta(minutes=15))
    refresh_token = jwt_token.create_refresh_token(data={"sub": user_info['sub']})

    firebase_token = None
    if db_user:
        firebase_token = auth.create_custom_token(db_user.firebase_uuid)

    return {"access_token": access_token, "refresh_token": refresh_token, "firebase_token": firebase_token}


@router.post("/login/apple/auth", tags=["Authentication"])
async def apple_auth(auth_schema: AuthSchema = Body(...), token: str = Header(), db: Session = Depends(get_db)):
    id_info = await jwt_token.verify_apple_token(token)

    user_info = dict(id_info)
    db_user = user_crud.get_user_by_uuid(db, user_info['sub'])

    if auth_schema.nick_name:
        if db_user is not None:
            if datetime.now() < db_user.deletion_date:
                raise HTTPException(status_code=400, detail="Cannot re-register within 7 days after deletion.")
        else:
            db_user = user_crud.create_user_kakao(db, user_info=user_info, auth_schema=auth_schema)

    else:
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if db_user.deletion_date is not None:
            raise HTTPException(status_code=404, detail="User not found")

        user_crud.update_fcm_token(db, db_user=db_user, token=auth_schema.fcm_token)

    # 토큰 생성
    access_token = jwt_token.create_access_token(data={"sub": user_info['sub']}, expires_delta=timedelta(minutes=15))
    refresh_token = jwt_token.create_refresh_token(data={"sub": user_info['sub']})

    firebase_token = None
    if db_user:
        firebase_token = auth.create_custom_token(db_user.firebase_uuid)

    return {"access_token": access_token, "refresh_token": refresh_token, "firebase_token": firebase_token}


@router.delete("/account/google/delete", tags=["Authentication"])
async def google_revoke(uuid: str = Header(), db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_uuid(db, uuid=uuid)

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_crud.mark_user_to_delete(db, db_user=db_user)


@router.delete("/account/kakao/delete", tags=["Authentication"])
async def kakao_revoke(uuid: str = Header(), db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_uuid(db, uuid=uuid)

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_crud.mark_user_to_delete(db, db_user=db_user)


@router.delete("/account/apple/delete", tags=["Authentication"])
async def apple_revoke(token: str = Header(), auth_code: str = Header(), db: Session = Depends(get_db)):
    id_info = await jwt_token.verify_apple_token(token)

    user_info = dict(id_info)
    db_user = user_crud.get_user_by_uuid(db, user_info['sub'])

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    response_code = await jwt_token.revoke_apple_token(auth_code)

    if response_code == 200:
        user_crud.mark_user_to_delete(db, db_user=db_user)
    else:
        raise HTTPException(status_code=400, detail="Failed to revoke token")


@router.post("/token/refresh", tags=["Authentication"])
async def token_refresh(token: str = Header(...), db: Session = Depends(get_db)):
    payload = jwt_token.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_uuid = payload.get("sub")
    user = user_crud.get_user_by_uuid(db, user_uuid)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    access_token_expires = timedelta(minutes=15)  # Set the access token expiry time
    new_access_token = jwt_token.create_access_token(data={"sub": user_uuid}, expires_delta=access_token_expires)

    return {"access_token": new_access_token, "token_type": "bearer"}