from datetime import datetime, timedelta

from fastapi import FastAPI, Request, Depends, HTTPException, Header, Body
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from database import get_db
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from fastapi_sso.sso.kakao import KakaoSSO
from firebase_admin import auth

import jwt_token
from utils import db_utils
from domain.user import user_crud
from domain.user.user_schema import AuthSchema
from domain.post import post_router
from domain.comment import comment_router
from domain.like import like_router
from domain.user import user_router
from domain.board import board_router
from domain.accompany import accompany_router
from domain.bookmark import bookmark_router
from domain.report import report_router
from domain.chat import chat_router
from domain.notification import notification_router
from domain.block import block_router
from domain.vocabulary import vocabulary_router
from domain.admin import admin_router

load_dotenv()

origins = [
    "*",
]

app = FastAPI()

SECRET_KEY = os.getenv("SECRET_KEY")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="/mos-server/static"), name="static")
#app.mount("/static", StaticFiles(directory="static"), name="static")

sso = KakaoSSO(
    client_id=os.getenv("KAKAO_CLIENT_ID"),
    client_secret=os.getenv("KAKAO_CLIENT_SECRET"),
    #redirect_uri="http://127.0.0.1:8000/login/kakao/callback",
    redirect_uri="http://ec2-13-125-254-93.ap-northeast-2.compute.amazonaws.com:8000/login/kakao/callback",
    allow_insecure_http=True,
)


@app.get("/login/kakao", tags=["Test"])
async def kakao_login():
    """Initialize auth and redirect"""
    with sso:
        return await sso.get_login_redirect()


@app.get("/login/kakao/callback", tags=["Test"])
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


@app.get("/", response_class=HTMLResponse)
async def main():
    return HTMLResponse(content="<h1>환영합니다</h1>", status_code=200)


@app.post("/login/google/auth", tags=["Authentication"])
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


@app.post("/login/kakao/auth", tags=["Authentication"])
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


@app.post("/login/apple/auth", tags=["Authentication"])
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


@app.delete("/account/google/delete", tags=["Authentication"])
async def google_revoke(uuid: str = Header(), db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_uuid(db, uuid=uuid)

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_crud.mark_user_to_delete(db, db_user=db_user)


@app.delete("/account/kakao/delete", tags=["Authentication"])
async def kakao_revoke(uuid: str = Header(), db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_uuid(db, uuid=uuid)

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_crud.mark_user_to_delete(db, db_user=db_user)


@app.delete("/account/apple/delete", tags=["Authentication"])
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


@app.post("/token/refresh", tags=["Authentication"])
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


scheduler = BackgroundScheduler()
scheduler.add_job(db_utils.delete_blinded_contents, 'cron', hour=0, minute=0)
scheduler.add_job(user_crud.delete_user_sso, 'cron', hour=0, minute=0)
scheduler.start()

app.include_router(post_router.router)
app.include_router(comment_router.router)
app.include_router(like_router.router)
app.include_router(user_router.router)
app.include_router(board_router.router)
app.include_router(accompany_router.router)
app.include_router(bookmark_router.router)
app.include_router(report_router.router)
app.include_router(chat_router.router)
app.include_router(notification_router.router)
app.include_router(block_router.router)
app.include_router(vocabulary_router.router)
app.include_router(admin_router.router)