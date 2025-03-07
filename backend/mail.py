from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType


from config import Config
from pathlib import Path



BASE_DIR= Path(__file__).resolve().parent


conf = ConnectionConfig(

    MAIL_USERNAME =Config.MAIL_USERNAME,
    MAIL_PASSWORD = Config.MAIL_PASSWORD,
    MAIL_FROM = Config.MAIL_FROM,
    MAIL_PORT = Config.MAIL_PORT,
    MAIL_SERVER = Config.MAIL_SERVER,
    MAIL_STARTTLS = Config.MAIL_STARTTLS,
    MAIL_SSL_TLS = Config.MAIL_SSL_TLS,
    USE_CREDENTIALS = Config.USE_CREDENTIALS,
    VALIDATE_CERTS = Config.VALIDATE_CERTS,
    TEMPLATE_FOLDER= Path(BASE_DIR, 'templates')
)


mail = FastMail(
    config= conf
)


def CreateMessage(recipient:list[str], subject:str, body:str):
    message = MessageSchema(
        recipients=recipient,
        subject=subject,
        body=body,
        subtype= MessageType.html
    )

    return message


