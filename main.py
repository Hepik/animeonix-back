from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from utils.innit_db import create_tables
from dotenv import load_dotenv
import os
from controllers import title, review

create_tables()

load_dotenv()
IMAGE_DIR = os.getenv("IMAGE_DIR")

app = FastAPI()
app.mount("/images", StaticFiles(directory=IMAGE_DIR), name="images")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(title.router)
app.include_router(review.router)
