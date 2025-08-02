# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
# from django.contrib.auth import get_user_model
# from rest_framework_simplejwt.tokens import RefreshToken
# from django.views.decorators.csrf import csrf_exempt
# from .serializers import SendOTPSerializer, VerifyOTPSerializer
# from .services import send_otp_via_beem, verify_otp_via_beem
# from django.utils.decorators import method_decorator
# from rest_framework.views import APIView
# from myapp.models import *


# @method_decorator(csrf_exempt, name='dispatch')
# class SendOTPView(APIView):
#     def post(self, request):
#         serializer = SendOTPSerializer(data=request.data)
#         if serializer.is_valid():
#             phone = serializer.validated_data['phone']
#             try:
#                 user = CustomUser.objects.get(phone=phone)
#             except CustomUser.DoesNotExist:
#                 return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

#             res = send_otp_via_beem(phone)
#             return Response(res.json(), status=res.status_code)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# @api_view(['POST'])
# def verify_otp(request):
#     serializer = VerifyOTPSerializer(data=request.data)
#     if serializer.is_valid():
#         res = verify_otp_via_beem(
#             serializer.validated_data['pinId'],
#             serializer.validated_data['pin']
#         )

#         if res.status_code == 200 and res.json().get("valid"):
#             try:
#                 user = CustomUser.objects.get(phone=request.data.get('phone'))
#             except CustomUser.DoesNotExist:
#                 return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 "token": str(refresh.access_token),
#                 "refresh": str(refresh),
#                 "user": {
#                     "id": user.id,
#                     "phone": user.phone,
#                     "username": user.username,
#                 }
#             })

#         return Response({"error": "Invalid PIN or verification failed."}, status=400)

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt

from .serializers import SendOTPSerializer, VerifyOTPSerializer
from .services import send_otp_via_beem

User = get_user_model()

@csrf_exempt  # remove this in production
@api_view(['POST'])
def send_otp(request):
    serializer = SendOTPSerializer(data=request.data)
    if serializer.is_valid():
        phone = serializer.validated_data['phone']

        res = send_otp_via_beem(phone)
        return Response(res.json(), status=res.status_code)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
def verify_otp(request):
    serializer = VerifyOTPSerializer(data=request.data)
    if serializer.is_valid():
        pin_id = serializer.validated_data['pinId']
        pin = serializer.validated_data['pin']
        phone = serializer.validated_data['phone']

        res = verify_otp_via_beem(pin_id, pin)

        if res.status_code == 200 and res.json().get("valid"):
            try:
                user = User.objects.get(phone=phone)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            refresh = RefreshToken.for_user(user)
            return Response({
                "token": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "phone": user.phone,
                    "username": user.username,
                }
            })

        return Response({"error": "Invalid PIN or verification failed."}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
