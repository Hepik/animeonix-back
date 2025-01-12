from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.innit_db import create_tables
from controllers import title, review, auth, user, reaction
from dotenv import load_dotenv
import os

load_dotenv()
PORT = int(os.environ["PORT"])
FRONTEND_URL = os.environ["FRONTEND_URL"]
STATIC_DIR = os.environ["STATIC_DIR"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(title.router)
app.include_router(review.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(reaction.router)

if __name__ == "__main__":
    create_tables()
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
