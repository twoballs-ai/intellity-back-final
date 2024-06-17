import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..config import settings

async def send_welcome_email(email_to: str, name: str, role: str):
    subject = "Добро пожаловать в нашу платформу!"
    body = f"""
    <h1>Здравствуйте, {name}!</h1>
    <p>Вы успешно зарегистрированы как {role} на нашей платформе.</p>
    <p>Желаем вам успехов!</p>
    """

    message = MIMEMultipart()
    message["From"] = settings.MAIL_FROM
    message["To"] = email_to
    message["Subject"] = subject

    message.attach(MIMEText(body, "html"))

    smtp = aiosmtplib.SMTP(
        hostname=settings.MAIL_SERVER,
        port=settings.MAIL_PORT,
        use_tls=settings.MAIL_TLS,
    )

    await smtp.connect()
    await smtp.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
    await smtp.send_message(message)
    await smtp.quit()