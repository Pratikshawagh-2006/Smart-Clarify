import smtplib
import random
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(to_email: str, otp: str) -> bool:
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = "Smart Clarify - Email Verification OTP"

    body = f"""Hello,

Your OTP for Smart Clarify email verification is: {otp}

This OTP is valid for 10 minutes. If you did not request this, please ignore this email.

- Smart Clarify Team
"""
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send OTP email: {e}")
        return False