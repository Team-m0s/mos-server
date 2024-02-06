from authlib.integrations.base_client import OAuthError
from fastapi import FastAPI, Request, Depends
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
        'redirect_url': 'http://39.113.43.239:8000/auth'
    }
)

sso = KakaoSSO(
    client_id=os.getenv("KAKAO_CLIENT_ID"),
    client_secret=os.getenv("KAKAO_CLIENT_SECRET"),
    redirect_uri="http://127.0.0.1:8000/auth/callback",
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

    user = token.get('userinfo')
    db_user = user_crud.get_user_by_email(db, user['email'])

    if db_user:
        request.session['user'] = dict(user)
        return RedirectResponse(url='/welcome', status_code=302)
    else:
        return HTMLResponse(content='<h1>사용자 정보가 없습니다.</h1>', status_code=404)


@app.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect"""
    with sso:
        return await sso.get_login_redirect()


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Verify login"""
    with sso:
        user = await sso.verify_and_process(request, params={"client_secret": os.getenv("KAKAO_CLIENT_SECRET")})
    if user:
        request.session['user'] = dict(user)
    return RedirectResponse(url='/welcome')


app.include_router(post_router.router)
app.include_router(comment_router.router)
app.include_router(like_router.router)
app.include_router(user_router.router)
