import requests
import base64
from django.conf import settings

def send_otp_via_beem(phone):
    url = "https://apiotp.beem.africa/v1/request"

    credentials = f"{settings.BEEM_API_KEY}:{settings.BEEM_SECRET_KEY}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {encoded_credentials}",
    }

    payload = {
        "appId": settings.BEEM_APP_ID,
        "msisdn": phone
    }

    response = requests.post(url, json=payload, headers=headers)
    return response


# import requests
# import base64
# from django.conf import settings

# def send_otp_via_beem(phone):
#     url = "https://apiotp.beem.africa/v1/request"

#     # Step 1: Prepare credentials
#     credentials = f"{settings.BEEM_API_KEY}:{settings.BEEM_SECRET_KEY}"
#     encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
#     print("Encoded credentials:", encoded_credentials)

#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Basic {encoded_credentials}",
#     }

#     # Step 2: Prepare payload
#     payload = {
#         "appId": int(settings.BEEM_APP_ID),  # ensure it's int
#         "msisdn": phone
#     }

#     print("Payload being sent to Beem:", payload)
#     print("Headers:", headers)

#     # Step 3: Send request
#     try:
#         response = requests.post(url, json=payload, headers=headers)
#         print("Response status code:", response.status_code)
#         print("Response content:", response.text)

#         response.raise_for_status()
#         return response
#     except requests.exceptions.RequestException as e:
#         print("Request to Beem failed:", str(e))
#         raise
