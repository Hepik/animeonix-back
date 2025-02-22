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
BACKEND_URL = os.environ["BACKEND_URL"]

if "PYTEST_CURRENT_TEST" not in os.environ:
    STATIC_DIR = Path(os.environ["STATIC_DIR"])
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

            if avatar != f'{BACKEND_URL}/static/default_user_avatar.jpg':
                relative_path = avatar.replace(f"{BACKEND_URL}/static/", "")
                old_path = STATIC_DIR / relative_path
                if old_path.exists():
                    old_path.unlink()

            file_path = AVATARS_DIR / filename
            image.save(file_path)
            file.file.close()

            file_path = '/' + file_path.relative_to(STATIC_DIR.parent).as_posix()
            avatar_url = BACKEND_URL + file_path

            user = UserUpdate(avatar=avatar_url)

            return user
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading avatar: {str(e)}")
    

    def process_image(self, old_image_url: str, file: UploadFile = File(...)):
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

            if old_image_url != "":
                old_image_url = old_image_url[len(BACKEND_URL):]
                old_path = STATIC_DIR.parent / old_image_url.lstrip('/')
                old_path.unlink()

            file_path = TITLES_DIR / filename
            image.save(file_path)
            file.file.close()

            file_path = '/' + file_path.relative_to(STATIC_DIR.parent).as_posix()
            image_url = BACKEND_URL + file_path

            return image_url
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")
