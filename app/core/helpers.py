from urllib.parse import urlparse
import secrets
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

def valid_length(value, min_len, max_len, field_name):
    if not (min_len <= len(value) <= max_len):
        return False, f"{field_name} must be between {min_len} and {max_len} characters."

    return True, None

def is_safe_url(target):
    return urlparse(target).netloc == ''

def generate_otp(length=6):
    return ''.join(str(secrets.randbelow(10)) for _ in range(length))

def send_otp_email(receiver_email):
    sender_email = os.getenv("EMAIL_USER")
    app_password = os.getenv("EMAIL_PASS")

    if not sender_email or not app_password:
        raise ValueError("Email credentials are missing from environment variables.")

    otp_code = generate_otp()

    subject = "Your OTP Code"
    message = f"Your OTP code is: {otp_code}\nThis code will expire in 7 minutes."

    text = f"Subject: {subject}\n\n{message}"

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, text)

    return otp_code