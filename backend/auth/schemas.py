
from typing import List, Annotated
from books.schemas import BookModel
from reviews.schemas import ReviewModel
from pydantic import BaseModel, Field, EmailStr, field_validator, constr
from pydantic.types import StringConstraints
from datetime import  datetime
import uuid, re


UsernameType = Annotated[str, StringConstraints(min_length=3, max_length=50, pattern=r"^[\w.@+-]+$")]
PasswordType = Annotated[str, StringConstraints(min_length=8, max_length=100)]
PASSWORD_REGEX = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

class UserCreateModel(BaseModel):
    username: UsernameType
    email: EmailStr
    password: PasswordType

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not re.match(PASSWORD_REGEX, value):
            raise ValueError("Password must have at least 8 characters, including a number, a special character, and a mix of uppercase/lowercase.")
        return value
    
class UserModel(BaseModel):
    id: uuid.UUID 
    username : str
    email : EmailStr 
    first_name : str
    last_name : str
    role: str
    is_verified : bool 
    password_hash : str = Field(exclude= True)
    created_at : datetime 
    updated_at : datetime 
    books: List[BookModel]


class UserResponseModel(BaseModel):
    id: uuid.UUID 
    username : str
    email : EmailStr 
    is_verified : bool 
    password_hash : str = Field(exclude= True)
    created_at : datetime 
    updated_at : datetime 

class UserLoginModel(BaseModel):
      username: UsernameType
      password: PasswordType


class UserViewModel(BaseModel):
    id: uuid.UUID 
    username : str
    email : EmailStr 
    role: str
    is_verified : bool
    books: List[BookModel]
    reviews : List[ReviewModel]


class EmailModel(BaseModel):
    email_addresses : List[EmailStr]

class PasswordResetRequestModel(BaseModel):
    email : EmailStr

class PasswordResetConfirmModel(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password", "confirm_password")
    def validate_password(cls, value):
        if not re.match(PASSWORD_REGEX, value):
            raise ValueError("Password must have at least 8 characters, including a number, a special character, and a mix of uppercase/lowercase.")
        return value

