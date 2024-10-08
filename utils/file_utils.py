import os
import hashlib
from fastapi import FastAPI, File, UploadFile
from fastapi import HTTPException
from uuid import uuid4


def save_image_file(image_file: UploadFile):
    try:
        file_extension = os.path.splitext(image_file.filename)[1]
        file_name = f"{uuid4()}{file_extension}"  # 고유한 파일명 생성
        file_path = f"uploaded_images/{file_name}"

        with open('/mos-server/static/' + file_path, "wb") as buffer:
            buffer.write(image_file.file.read())

        image_file.file.seek(0)
        return file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save error: {e}")


def delete_image_file(image_path: str):
    try:
        os.remove('/mos-server/static/' + image_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File delete error: {e}")


def calculate_image_hash(image_file: UploadFile):
    image_data = image_file.file.read()
    image_hash = hashlib.sha256(image_data).hexdigest()
    image_file.file.seek(0)  # 파일 포인터를 시작 위치로 되돌림
    return image_hash
