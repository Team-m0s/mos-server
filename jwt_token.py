import json
import os
import requests
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from dotenv import load_dotenv
import httpx
from jwt.algorithms import RSAAlgorithm

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID_IOS")
KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID_IOS")
APPLE_CLIENT_ID = os.getenv("APPLE_CLIENT_ID")
PRIVATE_KEY_PATH = "AuthKey_62928X3S83.p8"

with open(PRIVATE_KEY_PATH, "r") as file:
    private_key = file.read()

kakao_jwks_cache = {}
apple_jwks_cache = {}


async def get_kakao_jwks(force_update=False):
    url = "https://kauth.kakao.com/.well-known/jwks.json"
    if 'jwks' in kakao_jwks_cache and not force_update:
        return kakao_jwks_cache['jwks']
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        jwks = response.json()
        kakao_jwks_cache['jwks'] = jwks
        return jwks


async def find_kakao_key_by_kid(kid):
    jwks = await get_kakao_jwks()
    for jwk in jwks.get('keys', []):
        if jwk.get('kid') == kid:
            return RSAAlgorithm.from_jwk(json.dumps(jwk))
    # 키를 찾지 못한 경우, 캐시를 클리어하고 JWKS 데이터를 다시 받아옵니다.
    jwks = await get_kakao_jwks(force_update=True)
    for jwk in jwks.get('keys', []):
        if jwk.get('kid') == kid:
            return RSAAlgorithm.from_jwk(json.dumps(jwk))
    return None


async def get_apple_jwks(force_update=False):
    url = "https://appleid.apple.com/auth/keys"
    if 'jwks' in apple_jwks_cache and not force_update:
        return apple_jwks_cache['jwks']
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        jwks = response.json()
        apple_jwks_cache['jwks'] = jwks
        return jwks


def get_apple_token(client_secret: str, auth_code: str):
    url = "https://appleid.apple.com/auth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "client_id": os.getenv("APPLE_CLIENT_ID"),
        "client_secret": client_secret,
        "code": auth_code,
        "grant_type": "authorization_code",
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        tokens = response.json()
        return tokens
    else:
        print("Error:", response.text)


async def revoke_apple_token(auth_code: str):
    client_secret = create_apple_client_secret()
    tokens = get_apple_token(client_secret, auth_code)
    access_token = tokens.get("access_token", None)
    refresh_token = tokens.get("refresh_token", None)

    url = "https://appleid.apple.com/auth/revoke"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "client_id": os.getenv("APPLE_CLIENT_ID"),
        "client_secret": client_secret,
        "token": access_token,
        "token_type_hint": "access_token",
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to revoke access token")

    url = "https://appleid.apple.com/auth/revoke"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "client_id": os.getenv("APPLE_CLIENT_ID"),
        "client_secret": client_secret,
        "token": refresh_token,
        "token_type_hint": "refresh_token",
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to revoke refresh token")

    return response.status_code


async def find_apple_key_by_kid(kid):
    jwks = await get_apple_jwks()
    for jwk in jwks.get('keys', []):
        if jwk.get('kid') == kid:
            return RSAAlgorithm.from_jwk(json.dumps(jwk))
    # 키를 찾지 못한 경우, 캐시를 클리어하고 JWKS 데이터를 다시 받아옵니다.
    jwks = await get_apple_jwks(force_update=True)
    for jwk in jwks.get('keys', []):
        if jwk.get('kid') == kid:
            return RSAAlgorithm.from_jwk(json.dumps(jwk))
    return None


async def verify_kakao_token(token: str):
    # ID 토큰의 영역 구분자인 온점(.)을 기준으로 헤더, 페이로드, 서명을 분리
    try:
        header, payload, signature = token.split('.')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token format")

    try:
        payload_data = jwt.get_unverified_claims(token)
    except (ValueError, JWTError):
        raise HTTPException(status_code=400, detail="Payload decoding failed")

    # 페이로드의 iss 값이 https://kauth.kakao.com와 일치하는지 확인
    if payload_data.get('iss') != "https://kauth.kakao.com":
        raise HTTPException(status_code=401, detail="Invalid issuer")

    # 페이로드의 aud 값이 서비스 앱 키와 일치하는지 확인
    if payload_data.get('aud') != os.getenv("KAKAO_CLIENT_ID_IOS"):
        raise HTTPException(status_code=401, detail="Invalid audience")

    # 페이로드의 exp 값이 현재 UNIX 타임스탬프보다 큰 값인지 확인
    if int(payload_data.get('exp')) < datetime.now().timestamp():
        raise HTTPException(status_code=401, detail="Token has expired")

    header_data = jwt.get_unverified_header(token)

    # JWKS를 가져온 후, 헤더의 kid에 해당하는 공개키를 찾음
    public_key = await find_kakao_key_by_kid(header_data.get('kid'))
    if not public_key:
        raise HTTPException(status_code=401, detail="Public key not found for the given kid")

    # JWT 서명 검증
    try:
        decoded_payload = jwt.decode(token, public_key, algorithms=["RS256"], audience=os.getenv("KAKAO_CLIENT_ID_IOS"))
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Signature verification failed: " + str(e))

    return decoded_payload


async def verify_apple_token(token: str):
    try:
        header, payload, signature = token.split('.')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token format")

    try:
        payload_data = jwt.get_unverified_claims(token)
    except (ValueError, JWTError):
        raise HTTPException(status_code=400, detail="Payload decoding failed")

    if payload_data.get('iss') != "https://appleid.apple.com":
        raise HTTPException(status_code=401, detail="Invalid issuer")

    # 페이로드의 aud 값이 서비스 앱 키와 일치하는지 확인
    if payload_data.get('aud') != os.getenv("APPLE_CLIENT_ID"):
        raise HTTPException(status_code=401, detail="Invalid audience")

    # 페이로드의 exp 값이 현재 UNIX 타임스탬프보다 큰 값인지 확인
    if int(payload_data.get('exp')) < datetime.now().timestamp():
        raise HTTPException(status_code=401, detail="Token has expired")

    header_data = jwt.get_unverified_header(token)

    # JWKS를 가져온 후, 헤더의 kid에 해당하는 공개키를 찾음
    public_key = await find_apple_key_by_kid(header_data.get('kid'))
    if not public_key:
        raise HTTPException(status_code=401, detail="Public key not found for the given kid")

    # JWT 서명 검증
    try:
        decoded_payload = jwt.decode(token, public_key, algorithms=["RS256"], audience=os.getenv("APPLE_CLIENT_ID"))
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Signature verification failed: " + str(e))

    return decoded_payload


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)  # 기본 만료 시간 설정
    now = datetime.utcnow()
    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_apple_client_secret():
    header = {
        "alg": "ES256",
        "kid": os.getenv("APPLE_KEY_ID")
    }

    payload = {
        "iss": os.getenv("APPLE_TEAM_ID"),
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=60),
        "aud": "https://appleid.apple.com",
        "sub": os.getenv("APPLE_CLIENT_ID")
    }

    client_secret = jwt.encode(payload, private_key, algorithm="ES256", headers=header)

    return client_secret


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=30)  # Refresh token expires after 1 month
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token format")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while verifying the token: " + str(e))
