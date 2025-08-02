import requests
from django.conf import settings
import base64

def send_otp_via_beem(phone):
    url = "https://gateway.beem.africa/v1/otp/send"
    credentials = f"{settings.BEEM_APP_KEY}:{settings.BEEM_SECRET_KEY}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {encoded_credentials}",
    }
    payload = {
        "phoneNumber": phone,
        "language": "en"  # or your preferred language
    }
    return requests.post(url, json=payload, headers=headers)


def verify_otp_via_beem(pin_id, pin):
    url = "https://gateway.beem.africa/v1/otp/verify"
    credentials = f"{settings.BEEM_APP_KEY}:{settings.BEEM_SECRET_KEY}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {encoded_credentials}",
    }
    payload = {
        "pinId": pin_id,
        "pin": pin
    }
    return requests.post(url, json=payload, headers=headers)
