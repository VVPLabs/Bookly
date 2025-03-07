
from fastapi import APIRouter, Depends, status , BackgroundTasks
from .schemas import (
    UserCreateModel,
    UserViewModel,
    UserResponseModel,
    UserLoginModel,
    EmailModel,
    PasswordResetRequestModel,
    PasswordResetConfirmModel   
)
from celery_tasks import send_email
from .service import UserService
from .utils import (
    create_access_token,
    decode_token,
    generate_pass_hash,
    verify_pass,
    create_url_safe_token,
    decode_url_safe_token,
    validate_email,
)
from db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from .dependecies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker,
    sanitize_input,
)
from db.redis import add_jti_to_blocklist
from db.main import get_session
from config import Config
from mail import mail, CreateMessage


auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])


@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    email_list = emails.email_addresses

    html = "<h1>Welcome to app</h1>"

    send_email.delay(email_list, subject="welcome", body=html)


    return {"message": "Email sent successfully"}


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_account(
    user_data: UserCreateModel,bg_tasks: BackgroundTasks ,session: AsyncSession = Depends(get_session)
):
    email = user_data.email
    
    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with email already exists",
        )

    new_user = await user_service.create_user(user_data, session)

    token = create_url_safe_token({"email": email})

    link = f"{Config.DOMAIN}api/v1/auth/verify/{token}"
    html_message = f"""
    <h1> Verify Your Email</h1>
    <p> Please Click this<a href="{link}">link</a> to verify your email</p>
    """
    message = CreateMessage(
        recipient=[email], subject="Verify your Email", body=html_message
    )

    bg_tasks.add_task( mail.send_message, message)

    return {
        "message": "Account Created Successfully check email to verify account",
        "user": new_user,
    }


@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)
    if token_data is None:
        raise HTTPException(status_code=400, detail="Invalid token")
    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        await user_service.update_user(user, {"is_verified": True}, session)

        return {"message": "Account Verified Successfully", "user": user}
    return JSONResponse(
        content={
            "message": "Error occured during verification ",
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@auth_router.post("/login")
async def login_user(
    login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    username:str = login_data.username
    password:str = str(login_data.password)

    user = await user_service.get_user_by_username(username, session)

    if user is not None:
        password_valid = verify_pass(password, user.password_hash)

        if password_valid:
            access_token = create_access_token({"email": user.email, "user_uid": str(user.id), "role": user.role})

        
        refresh_token = create_access_token({"email": user.email, "user_uid": str(user.id)}, refresh=True, expiry=timedelta(days=2))

        response = JSONResponse(content={"message": "Login successful", "access_token": access_token})
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite='strict')

        return response
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="invalid username & password"
    )


@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])
        return JSONResponse(content={"access_token": new_access_token})
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="INVALID OR EXPIRED TOKEN"
    )


@auth_router.get("/me", response_model=UserViewModel)
async def get_me(user=Depends(get_current_user), _: bool = Depends(role_checker)):
    return user


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"Message": "LOGGED OUT SUCCESSFULLY"}, status_code=status.HTTP_200_OK
    )


@auth_router.post('/password-reset-request')
async def password_reset_request(email_data : PasswordResetRequestModel):
    email = email_data.email

    token = create_url_safe_token({"email": email})

    link = f"{Config.DOMAIN}api/v1/auth/password-reset-confirm/{token}"
    html_message = f"""
    <h1> Reset your password</h1>
    <p> Please Click this<a href="{link}">link</a> to reset your password</p>
    """
    message = CreateMessage(
        recipient=[email], subject="Verify your Email", body=html_message
    )

    await mail.send_message(message)

    return {
        "message": "Please check your email for instrauctions to reset your password",
        
    }

@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(token: str, passwords :PasswordResetConfirmModel , session: AsyncSession = Depends(get_session)):
    new_password= passwords.new_password
    confirm_password = passwords.confirm_password
    if new_password != confirm_password:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="passwords don't match")
    
    token_data = decode_url_safe_token(token)
    if token_data is None:
        raise HTTPException(status_code=400, detail="Invalid token")
    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        passwd_hash = generate_pass_hash(new_password)
        await user_service.update_user(user, {"password_hash": passwd_hash}, session)

        return {"message": "Password update successfully", "user": user}
    return JSONResponse(
        content={
            "message": "Error occured during password reset ",
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) 
