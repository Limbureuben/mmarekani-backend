import requests
from django.conf import settings

def send_otp_via_beem(phone):
    url = "https://gateway.beem.africa/v1/otp/send"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {settings.BEEM_APP_KEY}:{settings.BEEM_SECRET_KEY}"
    }
    payload = {
        "appId": settings.BEEM_APP_KEY,
        "msisdn": phone,
        "senderId": settings.BEEM_SENDER_ID,
    }
    response = requests.post(url, json=payload, headers=headers)
    return response

def verify_otp_via_beem(pin_id, pin):
    url = "https://gateway.beem.africa/v1/otp/verify"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {settings.BEEM_APP_KEY}:{settings.BEEM_SECRET_KEY}"
    }
    payload = {
        "pinId": pin_id,
        "pin": pin
    }
    response = requests.post(url, json=payload, headers=headers)
    return response
