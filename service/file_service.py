from fastapi import HTTPException, UploadFile, File
from PIL import Image
from schemas.user_schema import *
from schemas.title_schema import *
import hashlib
from pathlib import Path
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

if "PYTEST_CURRENT_TEST" not in os.environ:
    PUBLIC_DIR = Path(os.environ["PUBLIC_DIR"])
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    STATIC_DIR = PUBLIC_DIR / "static"
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

    TITLES_DIR = STATIC_DIR / "titles"
    TITLES_DIR.mkdir(parents=True, exist_ok=True)

    AVATARS_DIR = STATIC_DIR / "avatars"
    AVATARS_DIR.mkdir(parents=True, exist_ok=True)

class FileService:
    def process_avatar(self, avatar: str, file: UploadFile = File(...)):
        try:
            if file.content_type not in ["image/jpeg", "image/png"]:
                raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are allowed.")
            
            salt = uuid.uuid4().hex

            file_content = file.file.read()
            combined_content = file_content + salt.encode()
            file_hash = hashlib.sha1(combined_content).hexdigest()
            file.file.seek(0)

            image = Image.open(file.file)
            
            image.thumbnail((300, 300))
            
            extension = "jpg" if file.content_type == "image/jpeg" else "png"
            filename = f"{file_hash}.{extension}"

            if avatar != '/static/default_user_avatar.jpg':
                old_path = STATIC_DIR.parent / avatar.lstrip('/')
                old_path.unlink()

            file_path = AVATARS_DIR / filename
            image.save(file_path)
            file.file.close()

            file_path = '/' + file_path.relative_to(STATIC_DIR.parent).as_posix()

            user = UserUpdate(avatar=file_path)

            return user
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading avatar: {str(e)}")
    

    def process_image(self, old_image: str, file: UploadFile = File(...)):
        try:
            if file.content_type not in ["image/jpeg", "image/png"]:
                raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are allowed.")
            
            salt = uuid.uuid4().hex

            file_content = file.file.read()
            combined_content = file_content + salt.encode()
            file_hash = hashlib.sha1(combined_content).hexdigest()
            file.file.seek(0)

            image = Image.open(file.file)
            
            extension = "jpg" if file.content_type == "image/jpeg" else "png"
            filename = f"{file_hash}.{extension}"

            if old_image != "":
                old_path = STATIC_DIR.parent / old_image.lstrip('/')
                old_path.unlink()

            file_path = TITLES_DIR / filename
            image.save(file_path)
            file.file.close()

            file_path = '/' + file_path.relative_to(STATIC_DIR.parent).as_posix()

            return file_path
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")
