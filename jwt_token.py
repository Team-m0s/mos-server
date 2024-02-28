import json
import os
from jwt import PyJWTError
from fastapi import HTTPException
from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from dotenv import load_dotenv
import httpx
from jwt.algorithms import RSAAlgorithm

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID_IOS")
KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID_IOS")
APPLE_CLIENT_ID = os.getenv("APPLE_CLIENT_ID")

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

    print(payload_data)

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

    print(decoded_payload)
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
    except PyJWTError:
        return None
