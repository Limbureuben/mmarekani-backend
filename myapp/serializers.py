from rest_framework import serializers # type: ignore
from .models import *

# class RegisterUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ['username', 'phone', 'national_id']

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'phone', 'national_id', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Remove before saving
        user = CustomUser(
            username=validated_data['username'],
            phone=validated_data['phone'],
            national_id=validated_data['national_id'],
        )
        user.set_password(validated_data['password'])  # hash the password
        user.save()
        return user


class PhoneSerializer(serializers.Serializer):
    phone = serializers.CharField()

class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField()


class LoanApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = ['id', 'loan_amount', 'passport_picture', 'nida_picture', 'submitted_at', 'status']
        read_only_fields = ['submitted_at', 'status']
