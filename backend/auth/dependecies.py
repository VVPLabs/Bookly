from fastapi import Request, status, Depends
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.exceptions import HTTPException
from .utils import decode_token
from .service import UserService
from .schemas import UserCreateModel
from db.models import User
from db.redis import token_in_blocklist
from db.main import get_session
from markupsafe import escape
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List

user_service = UserService()



async def sanitize_input(user_data: UserCreateModel):
    
    user_data.username = escape(user_data.username)
    user_data.email = user_data.email.strip().lower()
    return user_data

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        creds = await super().__call__(request)
        if creds is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No credentials provided"
            )

        token = creds.credentials

        token_data = decode_token(token)
        
        if not self.token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "THIS TOKEN IS INVALID OR EXPIRED",
                    "resolution": "PLEASE GET NEW TOKEN"
                }
            )
        
        if await token_in_blocklist(token_data['jti']):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail={
                    "error": "THIS TOKEN IS INVALID OR HAS BEEN REVOKED",
                    "resolution": "PLEASE GET NEW TOKEN"
                }
            )

        self.verify_token_data(token_data)

        return token_data

    def token_valid(self, token: str) -> bool:
      
        try:
            token_data = decode_token(token)
            return token_data is not None
        except Exception:
            return False  

    def verify_token_data(self, token_data: dict) -> None:
        
        raise NotImplementedError("please override in child class")

class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        
        if token_data and token_data.get('refresh', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="PROVIDE A VALID ACCESS TOKEN"
            )

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data.get('refresh', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="PROVIDE A VALID REFRESH TOKEN"
            )


async def get_current_user(
        token_details: dict=Depends(AccessTokenBearer()), 
        session : AsyncSession= Depends(get_session) ):
    
    user_info = token_details.get('user')

    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    user_email = user_info.get('email')
    if not user_email:
        raise HTTPException(status_code=401, detail="Email missing in token")
    
    user = await user_service.get_user_by_email(user_email, session)
    return  user


class RoleChecker:
    def __init__(self, allowed_roles:List[str]):
        self.allowed_role = allowed_roles

    def __call__(self, current_user:User= Depends(get_current_user)):
        if not current_user.is_verified:
            raise HTTPException(
                status_code= status.HTTP_403_FORBIDDEN,
                detail= {
                    "message": "Account not verified",
                    "resolution": "Please check your email for verification "
                }
            )
        
        if current_user.role in self.allowed_role:
            return True
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail= "YOU ARE NOT PERMITTED TO PERFORM THIS ACTION"
        ) 

