import smtplib
from email.message import EmailMessage
from app.config import SMTP_HOST, SMTP_PORT

def send_verification_email(to_email: str, token: str):
    msg = EmailMessage()
    verify_link = f"http://localhost:8000/auth/verify?token={token}"
    msg["Subject"] = "Verify your email"
    msg["From"] = "no-reply@example.com"
    msg["To"] = to_email
    msg.set_content(f"Click to verify: {verify_link}")
    with smtplib.SMTP(SMTP_HOST, int(SMTP_PORT)) as s:
        s.send_message(msg)
