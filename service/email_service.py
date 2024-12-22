from fastapi import HTTPException, Depends
from typing import Annotated
from schemas.user_schema import *
from repository.user_repository import UserRepository
from dotenv import load_dotenv
import os
import bcrypt
import jwt
from datetime import timedelta, datetime, timezone
from starlette import status
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = 'HS256'
SMTP_SERVER = os.environ["SMTP_SERVER"]
SMTP_PORT = int(os.environ["SMTP_PORT"])
SENDER_EMAIL = os.environ["SENDER_EMAIL"]
SENDER_PASSWORD = os.environ["SENDER_PASSWORD"]

class EmailService:
    def __init__(self, repository: Annotated[UserRepository, Depends()]):
        self.repository = repository

    def create_user_activation_token(self, user_id: int, expires_delta: timedelta):
        expires = datetime.now(timezone.utc) + expires_delta
        encode = {
            'sub_id': user_id,
            'type': "user_activation",
            'exp': expires,
            }
        x = jwt.encode(encode, SECRET_KEY, ALGORITHM)
        print('Activation Token:', x)
        return x
    
    def send_email(self, activation_token: str, recipient_email: str, recipient_username: str):
        subject = "Activate Your Account"
        body = f"""\
        Hello, {recipient_username}!

        Thank you for signing up for AnimeOnix. Please click the link below to activate your account:

        http://localhost:3000/login?activation_token={activation_token}

        If you did not sign up for this account, please ignore this email.

        Best regards,
        Your AnimeOnix
        """
        message = MIMEMultipart()
        message['From'] = SENDER_EMAIL
        message['To'] = recipient_email
        message['Subject'] = subject

        message.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)

            server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())


    def check_activation_token(self, activation_token: str):
        try:
            payload = jwt.decode(activation_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = payload.get('sub_id')
            self.repository.activate_user_profile(user_id)
            return {"detail": "account activated successfully"}
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired."
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Token is not valid."
            )
