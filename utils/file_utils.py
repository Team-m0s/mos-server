import os
from fastapi import FastAPI, File, UploadFile
from fastapi import HTTPException
from uuid import uuid4


def save_image_file(image_file: UploadFile):
    try:
        file_extension = os.path.splitext(image_file.filename)[1]
        file_name = f"{uuid4()}{file_extension}"  # 고유한 파일명 생성
        file_path = f"./uploaded_images/{file_name}"

        with open(file_path, "wb") as buffer:
            buffer.write(image_file.file.read())
        return file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save error: {e}")