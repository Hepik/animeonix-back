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
FRONTEND_URL = os.environ["FRONTEND_URL"]

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
        return jwt.encode(encode, SECRET_KEY, ALGORITHM)
    
    def create_password_reset_token(self, user_id: int, expires_delta: timedelta):
        expires = datetime.now(timezone.utc) + expires_delta
        encode = {
            'sub_id': user_id,
            'type': "password_reset",
            'exp': expires,
            }
        return jwt.encode(encode, SECRET_KEY, ALGORITHM)
    
    def send_email(self, activation_token: str, recipient_email: str, recipient_username: str):
        subject = "Activate Your Account"
        body = f"""\
        Hello, {recipient_username}!

        Thank you for signing up for AnimeOnix. Please click the link below to activate your account:

        {FRONTEND_URL}/login?activation_token={activation_token}

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


    def send_reset_password_email(self, reset_password_token: str, recipient_email: str, recipient_username: str):
        subject = "Password Reset Request"
        body = f"""\
        Hello, {recipient_username}!

        We received a request to reset the password for your account on AnimeOnix. If this was you, please click the link below to reset your password:

        {FRONTEND_URL}/login/reset-password?reset_password_token={reset_password_token}

        If you did not make this request, please ignore this email—your password will remain unchanged.

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

    def check_reset_password_token(self, reset_password_token: str):
        try:
            payload = jwt.decode(reset_password_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = payload.get('sub_id')
            type: str = payload.get('type')
            if type != 'password_reset':
                raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Token is not valid."
                )
            return user_id
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
