from celery import Celery
from mail import CreateMessage, mail
from asgiref.sync import async_to_sync



c_app= Celery()

c_app.config_from_object('backend.config')


@c_app.task()
def send_email(recipients : list[str], subject:str, body :str ):
    message = CreateMessage(
        recipient=recipients, subject=subject, body=body
    )
    async_to_sync(mail.send_message)(message)
