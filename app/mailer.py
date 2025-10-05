import os
from email.message import EmailMessage
import smtplib

SMTP_HOST = os.getenv("SMTP_HOST", "mailhog")
SMTP_PORT = int(os.getenv("SMTP_PORT", 1025))
FROM_EMAIL = os.getenv("FROM_EMAIL", "no-reply@example.com")
APP_HOST = os.getenv("APP_HOST", "http://localhost:8000")

def send_verification_email(to_email: str, token: str):
    verify_link = f"{APP_HOST}/auth/verify?token={token}"
    msg = EmailMessage()
    msg["Subject"] = "Verify your email"
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg.set_content(f"Click to verify: {verify_link}")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.send_message(msg)

def send_reset_email(to_email: str, token: str):
    reset_link = f"{APP_HOST}/auth/reset-password?token={token}"
    msg = EmailMessage()
    msg["Subject"] = "Reset your password"
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg.set_content(f"Click to reset your password: {reset_link}")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.send_message(msg)