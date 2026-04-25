from urllib.parse import urlparse
from datetime import datetime
import secrets
import resend
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
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        raise ValueError("RESEND_API_KEY is missing from environment variables.")

    resend.api_key = api_key

    otp_code = generate_otp()

    html_content = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2>PharmaHive Verification</h2>
        <p>Your OTP code is:</p>
        <h1 style="letter-spacing: 2px;">{otp_code}</h1>
        <p>This code will expire in 7 minutes.</p>
    </div>
    """

    try:
        response = resend.Emails.send({
            "from": "PharmaHive <noreply@mail.pharmahive.xyz>",
            "to": [receiver_email],
            "subject": "Your OTP Code",
            "html": html_content
        })
        return otp_code

    except Exception as e:
        print("EMAIL ERROR:", repr(e))
        raise
    
def is_valid_otp(otp):
    now =  datetime.utcnow()

    if not otp:
        return False
    
    if otp.expires_at < now:
        return False

    return True