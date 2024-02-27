import json
import os
import asyncio
from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import FastAPI, HTTPException
from jose import jwt, JWTError
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import httpx
from jwt.algorithms import RSAAlgorithm

load_dotenv()

# request = requests.Request()
#
# token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjZmOTc3N2E2ODU5MDc3OThlZjc5NDA2MmMwMGI2NWQ2NmMyNDBiMWIiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiI1MTkzNTQyMjIxNzctcjVobzczNmY5YXBscTJ1cnFpcDdqaHFoNmxqMGl2cTMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI1MTkzNTQyMjIxNzctcjVobzczNmY5YXBscTJ1cnFpcDdqaHFoNmxqMGl2cTMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDI3MzYxMDAwNTAwNzA0Mzk5ODciLCJlbWFpbCI6IndsZ25zZGw4MTVAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImF0X2hhc2giOiJQbkdHTWk0MC15ZjAxUjRQZ0szM0h3Iiwibm9uY2UiOiJ5U25fZ1pveGNnZVc3ZGFlblgwUUxFNURoUktVQVBYbENtOUJsTE55bjA4IiwibmFtZSI6IkppaG9vbiBQYXJrIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0lESmY0azVVOHFRZzF2X1RyLV95Smc3RVRmOEkwRkR6dW1yQXFqSzJPVT1zOTYtYyIsImdpdmVuX25hbWUiOiJKaWhvb24iLCJmYW1pbHlfbmFtZSI6IlBhcmsiLCJsb2NhbGUiOiJrbyIsImlhdCI6MTcwOTAyODc3MywiZXhwIjoxNzA5MDMyMzczfQ.KWso5vn_b_dfc0-Hu8yqRhZbZbwghb1vM5Kh0cYZndco7YWC--C-uOu1_zIIN-Zr4mvtNnQs_XfyHRDudiM4Pnf4jx82HoyW3dXzmV4xlwHBsgNCDXdgKa32OOArRVS4KMZMnz_2008t7WcxSF7xmc2bsxJqXYB60qVkAl6zOomtTFc8n_rYkPrWGvtSgyOrhH8jMs4JChy1nxPtBFq2hWM1_BM_Eo36Uf6nnyAfAMbP2hki85R_jeSmJNxsvwzSNAioVyb0YYvqQiAM1d_JU6TpL5OE3ev5r_nbMoq71HNd3vGm82ce2wnkcQ8sxcA3A4J0_k_OKwchDHk3hSMySw"
# GOOGLE_CLIENT_ID = "519354222177-r5ho736f9aplq2urqip7jhqh6lj0ivq3.apps.googleusercontent.com"
#
# id_info = id_token.verify_oauth2_token(token, request, GOOGLE_CLIENT_ID)
# userid = dict(id_info)
#
# print(userid)


id_token = "eyJraWQiOiI5ZjI1MmRhZGQ1ZjIzM2Y5M2QyZmE1MjhkMTJmZWEiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI0NWNhYzlkYWU2MGYxODExYmFiNmJjNTcwM2U3YTY5YyIsInN1YiI6IjMzMzQyODc1MzQiLCJhdXRoX3RpbWUiOjE3MDkwMzA4MDcsImlzcyI6Imh0dHBzOi8va2F1dGgua2FrYW8uY29tIiwibmlja25hbWUiOiLsp4Dtm4giLCJleHAiOjE3MDkwNzQwMDcsImlhdCI6MTcwOTAzMDgwNywicGljdHVyZSI6Imh0dHA6Ly9rLmtha2FvY2RuLm5ldC9kbi8xRzlrcC9idHNBb3Q4bGlPbi84Q1d1ZGkzdXkwN3J2Rk5Va2szRVIwL2ltZ18xMTB4MTEwLmpwZyIsImVtYWlsIjoid2xnbnNkbDgxNUBuYXZlci5jb20ifQ.RFUjVKPgKqqwku8LPzfNJlIJKPXSaA_bmAZoRxvHhBGt84fsVsH5ALd1O1o-NxIeHMkOeG9EsIPXpjLhAJAuQyF6jbYiNfLMUrM-NoK2udabFFuk-MKv-5ReUcGa7MSj8lpxkAGCp8afcxbVRGiMneyd5BK32ybZjcCcgy7O9g_d49ET5rvfupDA6DWsny8NeftK-hkDxrPPGrZsrsYfCnPgPORf95Qm871GZPNFWbuUP1o3UrtT6O9aaaA7CsEcbBIqYr43_BmIgYbGk7VkI1IVWP0-2yfSlO3bZOS9WnnyQgI7V5v-GH7Yeu9rW9gmfPPLDsb5gV3erl69FDdclw"

jwks_cache = {}


async def get_jwks(force_update=False):
    url = "https://kauth.kakao.com/.well-known/jwks.json"
    if 'jwks' in jwks_cache and not force_update:
        return jwks_cache['jwks']
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        jwks = response.json()
        jwks_cache['jwks'] = jwks
        return jwks


async def find_key_by_kid(kid):
    jwks = await get_jwks()
    for jwk in jwks.get('keys', []):
        if jwk.get('kid') == kid:
            return RSAAlgorithm.from_jwk(json.dumps(jwk))
    # 키를 찾지 못한 경우, 캐시를 클리어하고 JWKS 데이터를 다시 받아옵니다.
    jwks = await get_jwks(force_update=True)
    for jwk in jwks.get('keys', []):
        if jwk.get('kid') == kid:
            return RSAAlgorithm.from_jwk(json.dumps(jwk))
    return None


async def verify_token(token: str):
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

    # 헤더를 Base64 방식으로 디코딩하여 Python 객체로 변환
    decoded_header = base64.urlsafe_b64decode(header + "==").decode('utf-8')
    header_data = jwt.get_unverified_header(token)

    # JWKS를 가져온 후, 헤더의 kid에 해당하는 공개키를 찾음
    public_key = await find_key_by_kid(header_data.get('kid'))
    if not public_key:
        raise HTTPException(status_code=401, detail="Public key not found for the given kid")

    # JWT 서명 검증
    try:
        decoded_payload = jwt.decode(token, public_key, algorithms=["RS256"], audience=os.getenv("KAKAO_CLIENT_ID_IOS"))
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Signature verification failed: " + str(e))

    print(decoded_payload)
    return {"message": "Token is valid and signature is verified"}


async def main():
    verified = await verify_token(id_token)
    print(verified)


if __name__ == "__main__":
    asyncio.run(main())
    print(jwks_cache)
