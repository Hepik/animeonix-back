import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.innit_db import create_tables
from controllers import title, review, auth, user, reaction
from dotenv import load_dotenv
import os

load_dotenv()
PORT = int(os.environ["PORT"])

create_tables()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(title.router)
app.include_router(review.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(reaction.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
