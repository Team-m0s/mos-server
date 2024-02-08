from datetime import timedelta
import logging
from authlib.integrations.base_client import OAuthError
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse, HTMLResponse, JSONResponse
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

load_dotenv()

origins = [
    "http://127.0.0.1:8000",
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

# 구글 클라이언트 설정
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    client_kwargs={
        'scope': 'email openid profile',
        # 'redirect_url': 'http://127.0.0.1:8000/auth'
    }
)

sso = KakaoSSO(
    client_id=os.getenv("KAKAO_CLIENT_ID"),
    client_secret=os.getenv("KAKAO_CLIENT_SECRET"),
    redirect_uri="http://127.0.0.1:8000/auth/callback",
    allow_insecure_http=True,
)


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    token = request.cookies.get('access_token')

    if token:
        payload = jwt_token.verify_token(token)
        if payload:
            return RedirectResponse(url='/welcome', status_code=302)

    html_content = """
    <html>
        <head>
            <title>Login with Google</title>
        </head>
        <body>
            <h2>Login with Google</h2>
            <a href="/login">Login</a>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/welcome", response_class=HTMLResponse)
async def welcome():
    return HTMLResponse(content="<h1>환영합니다</h1>", status_code=200)


@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get('/auth')
async def auth(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(content=f'<h1>{error.error}</h1>', status_code=400)

    user_info = token.get('userinfo')
    db_user = user_crud.get_user_by_email(db, user_info['email'])

    if db_user is None:
        user_crud.create_user(db, user_info=user_info)
        print("회원가입 완료")
    else:
        print("이미 가입된 회원")
        access_token_expires = timedelta(minutes=60)  # 토큰 유효 시간 설정
        access_token = jwt_token.create_access_token(data={"sub": user_info['email']},
                                                     expires_delta=access_token_expires)
        return JSONResponse(content={"access_token": access_token, "token_type": "bearer"})


@app.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect"""
    with sso:
        return await sso.get_login_redirect()


@app.get("/auth/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    """Verify login"""
    with sso:
        user = await sso.verify_and_process(request, params={"client_secret": os.getenv("KAKAO_CLIENT_SECRET")})

    user_info = dict(user)
    db_user = user_crud.get_user_by_email(db, user_info['email'])
    if db_user is None:
        user_crud.create_user(db, user_info=user_info)
        print("회원가입 완료")

    token_data = {"email": user_info["email"]}
    # 토큰 생성
    access_token = jwt_token.create_access_token(data=token_data)
    return {"access_token": access_token}


@app.get("/auth/logout")
async def auth_logout(request: Request):
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    return response


app.include_router(post_router.router)
app.include_router(comment_router.router)
app.include_router(like_router.router)
app.include_router(user_router.router)
