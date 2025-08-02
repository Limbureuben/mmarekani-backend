from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import SendOTPSerializer, VerifyOTPSerializer
from .services import send_otp_via_beem, verify_otp_via_beem

@api_view(['POST'])
def send_otp(request):
    serializer = SendOTPSerializer(data=request.data)
    if serializer.is_valid():
        phone = serializer.validated_data['phone']
        res = send_otp_via_beem(phone)
        return Response(res.json(), status=res.status_code)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def verify_otp(request):
    serializer = VerifyOTPSerializer(data=request.data)
    if serializer.is_valid():
        res = verify_otp_via_beem(
            serializer.validated_data['pinId'],
            serializer.validated_data['pin']
        )
        return Response(res.json(), status=res.status_code)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
