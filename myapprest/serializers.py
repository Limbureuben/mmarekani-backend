from rest_framework import serializers

class SendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

class VerifyOTPSerializer(serializers.Serializer):
    pinId = serializers.CharField()
    pin = serializers.CharField()
