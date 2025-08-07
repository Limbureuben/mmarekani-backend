import base64
import requests
from django.conf import settings

def send_otp_via_beem(phone: str, code: str) -> bool:
    url = "https://apiotp.beem.africa/v1/request"

    credentials = f"{settings.BEEM_API_KEY}:{settings.BEEM_SECRET_KEY}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json",
    }

    payload = {
        "source_addr": settings.BEEM_SENDER_ID,
        "encoding": "0",
        "schedule_time": "",
        "message": f"Your OTP code is {code}",
        "recipients": [{"recipient_id": 1, "dest_addr": phone}],
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Error sending OTP: {e}")
        return False
