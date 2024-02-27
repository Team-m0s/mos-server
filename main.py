from datetime import timedelta
from authlib.integrations.base_client import OAuthError
from fastapi import FastAPI, Request, Depends, HTTPException, Header
from authlib.integrations.starlette_client import OAuth
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from database import get_db
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from fastapi_sso.sso.kakao import KakaoSSO

import jwt_token
from domain.user import user_crud
from domain.post import post_router
from domain.comment import comment_router
from domain.like import like_router
from domain.user import user_router
from domain.board import board_router
from domain.accompany import accompany_router

load_dotenv()

origins = [
    "*",
]

app = FastAPI()

oauth = OAuth()

SECRET_KEY = os.getenv("SECRET_KEY")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# 구글 클라이언트 설정
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    client_kwargs={
        'scope': 'email openid profile',
    }
)

sso = KakaoSSO(
    client_id=os.getenv("KAKAO_CLIENT_ID"),
    client_secret=os.getenv("KAKAO_CLIENT_SECRET"),
    # redirect_uri="http://127.0.0.1:8000/login/kakao/auth",
    redirect_uri="http://ec2-13-125-254-93.ap-northeast-2.compute.amazonaws.com:8000/login/kakao/auth",
    allow_insecure_http=True,
)


@app.get("/", response_class=HTMLResponse)
async def main():
    html_content = """
    <html>
        <head>
            <title>Login with Google</title>
        </head>
        <body>
            <h2>Login with Google</h2>
            <a href="/login/google/auth">Login</a>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/welcome", response_class=HTMLResponse)
async def welcome():
    return HTMLResponse(content="<h1>환영합니다</h1>", status_code=200)


# @app.get("/login/google/auth", tags=["Google"], name="google_auth")
# async def google_auth(request: Request, db: Session = Depends(get_db)):
#     try:
#         token = await oauth.google.authorize_access_token(request)
#     except OAuthError as error:
#         return HTMLResponse(content=f'<h1>{error.error}</h1>', status_code=400)
#
#     user_info = token.get('userinfo')
#     db_user = user_crud.get_user_by_email(db, user_info['email'])
#
#     if db_user is None:
#         user_crud.create_user_google(db, user_info=user_info)
#         print("회원가입 완료")
#     else:
#         print("이미 가입된 회원")
#
#     access_token_expires = timedelta(minutes=15)  # 토큰 유효 시간 설정
#     access_token = jwt_token.create_access_token(data={"sub": user_info['email']},
#                                                  expires_delta=access_token_expires)
#     refresh_token = jwt_token.create_refresh_token(data={"sub": user_info['email']})
#
#     return JSONResponse(content={"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"})

@app.get("/login/google/auth", tags=["Google"], name="google_auth")
async def google_auth(request: requests.Request(), token: str = Header(), db: Session = Depends(get_db)):
    try:
        id_info = await id_token.verify_oauth2_token(token, request, os.getenv("GOOGLE_CLIENT_ID_IOS"))

        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token.")

    user_info = dict(id_info)
    db_user = user_crud.get_user_by_email(db, user_info['email'])

    if db_user is None:
        user_crud.create_user_google(db, user_info=user_info)
        print("회원가입 완료")
    else:
        print("이미 가입된 회원")

    access_token_expires = timedelta(minutes=15)  # 토큰 유효 시간 설정
    access_token = jwt_token.create_access_token(data={"sub": user_info['email']},
                                                 expires_delta=access_token_expires)
    refresh_token = jwt_token.create_refresh_token(data={"sub": user_info['email']})

    return JSONResponse(content={"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"})


APPLE_CLIENT_ID = os.getenv("APPLE_CLIENT_ID")
APPLE_REDIRECT_URL = os.getenv("REDIRECT_URI")


@app.get("/login/apple", tags=["Apple"])
async def apple_login():
    url = (
        "https://appleid.apple.com/auth/authorize"
        f"?client_id={APPLE_CLIENT_ID}"
        f"&redirect_uri={APPLE_REDIRECT_URL}"
        "&response_type=code id_token"
        "&scope=name%20email"
        "&response_mode=form_post"
    )


@app.get("/login/kakao/auth", tags=["Kakao"])
async def kakao_auth(request: Request, db: Session = Depends(get_db)):
    """Verify login"""
    with sso:
        user = await sso.verify_and_process(request, params={"client_secret": os.getenv("KAKAO_CLIENT_SECRET")})

    user_info = dict(user)
    db_user = user_crud.get_user_by_email(db, user_info['email'])

    if db_user is None:
        user_crud.create_user_kakao(db, user_info=user_info)

    # 토큰 생성
    access_token = jwt_token.create_access_token(data={"sub": user_info['email']}, expires_delta=timedelta(minutes=15))
    refresh_token = jwt_token.create_refresh_token(data={"sub": user_info['email']})

    return {"access_token": access_token, "refresh_token": refresh_token}


@app.post("/token/refresh", tags=["Authentication"])
async def token_refresh(token: str = Header(...), db: Session = Depends(get_db)):
    payload = jwt_token.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_email = payload.get("sub")
    user = user_crud.get_user_by_email(db, user_email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    access_token_expires = timedelta(minutes=15)  # Set the access token expiry time
    new_access_token = jwt_token.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    return {"access_token": new_access_token, "token_type": "bearer"}


app.include_router(post_router.router)
app.include_router(comment_router.router)
app.include_router(like_router.router)
app.include_router(user_router.router)
app.include_router(board_router.router)
app.include_router(accompany_router.router)
