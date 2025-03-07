
from datetime import timedelta
from datetime import datetime, timezone
import logging
from typing import Optional
import jwt, uuid
from itsdangerous import URLSafeTimedSerializer
from jwt.exceptions import ExpiredSignatureError, DecodeError
from fastapi import HTTPException
from passlib.context import CryptContext
from config import Config
from pydantic import BaseModel, EmailStr, ValidationError
import os





password_context = CryptContext(
    schemes=['bcrypt']

)
def generate_pass_hash(password: str):
    hash = password_context.hash(str(password))

    return hash

def verify_pass(password: str, hash:str):
    return password_context.verify(str(password), str(hash))

def validate_email(email: str) -> str:
    
    class EmailModel(BaseModel):
        email: EmailStr

    try:
        valid_email = EmailModel(email=email)
        return valid_email.email
    except ValidationError:
        raise ValueError("Invalid email address provided.")



def create_access_token(user_data: dict, expiry: Optional[timedelta]= None , refresh : Optional[bool] = False):
    

    if expiry is None:
        expiry = timedelta(minutes=60)

    payload = {}
    payload['user']= user_data
    payload['exp']= (datetime.now(timezone.utc) + expiry).timestamp()
    payload['jti']= str(uuid.uuid4())
    payload['refresh']= refresh



    token= jwt.encode(
        payload= payload,
        key= Config.JWT_SECRET,
        algorithm= Config.JWT_ALGORITHM
    )

    return token


def decode_token(token: str)->dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired. Please log in again.")
    except DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token. Please provide a valid token.")


serializer = URLSafeTimedSerializer(
        secret_key=Config.JWT_SECRET,
        salt="email.configuration"

    )


def create_url_safe_token(data: dict, expiry: int = 86400):  # Default expiry: 24 hours (86400 seconds)
    data["exp"] = expiry  # Add expiry time
    token = serializer.dumps(data)
    return token

def decode_url_safe_token(token: str, max_age: int = 86400):
    try:
        token_data = serializer.loads(token, max_age=max_age)  # Validate expiry
        return token_data
    except Exception as e:
        logging.error(f"Token decoding failed: {str(e)}")
        return None
