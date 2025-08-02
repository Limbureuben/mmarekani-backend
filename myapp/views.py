from django.shortcuts import render
import graphene
from commerce_dto.commerce import *
from commerce_dto.Response import *
from graphene_django import DjangoObjectType
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
from commerceBuilders.commerceBuilder import UserBuilder



# Create your views here.
class RegistrationMutation(graphene.Mutation):
    user = graphene.Field(RegistrationObject)
    output = graphene.Field(RegistrationResponse)

    class Arguments:
        input = RegistrationInputObject(required=True)

    def mutate(self, info, input):
        response = UserBuilder.register_user(input)
        return RegistrationMutation(user=response.user, output=response)


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "is_staff", "is_superuser")


class LoginUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserLoginObject)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, username, password):
        try:
            user = authenticate(username=username, password=password)

            if user is None:
                return LoginUser(success=False, message="Invalid credentials")
            
            if not isinstance(user, User):
                raise ValidationError("User is not a valid CustomUser instance.")

            # Create JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            user_data = UserLoginObject(
                id=user.id,
                username=user.username,
                token=access_token,
                isStaff=user.is_staff,
            )

            return LoginUser(
                user=user_data,
                success=True,
            )

        except Exception as e:
            return LoginUser(success=False, message=f"An error occurred: {str(e)}")








## OTP AUTHENTICATION
import requests # type: ignore


class RequestOTP(graphene.Mutation):
    pin_id = graphene.String()
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        phone = graphene.String(required=True)

    def mutate(self, info, phone):
        headers = {
            "Authorization": "Basic YOUR_BASE64_KEY",
            "Content-Type": "application/json"
        }

        payload = {
            "appId": "YOUR_APP_ID",  # optional depending on your config
            "msisdn": phone,
            "senderId": "BeemOTP",
            "channel": "sms"  # or "ussd", "email"
        }

        try:
            response = requests.post(
                "https://otp.beem.africa/v1/request", json=payload, headers=headers
            )
            data = response.json()

            if response.status_code == 200 and data.get("pinId"):
                return RequestOTP(
                    pin_id=data["pinId"],
                    success=True,
                    message="OTP sent successfully"
                )
            else:
                return RequestOTP(success=False, message=data.get("message", "Failed to send OTP"))
        except Exception as e:
            return RequestOTP(success=False, message=str(e))





# Verify OTP via Beem (Step 7–9)
class VerifyOTP(graphene.Mutation):
    verified = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        pin_id = graphene.String(required=True)
        pin = graphene.String(required=True)

    def mutate(self, info, pin_id, pin):
        headers = {
            "Authorization": "Basic YOUR_BASE64_KEY",
            "Content-Type": "application/json"
        }

        payload = {
            "pinId": pin_id,
            "pin": pin
        }

        try:
            response = requests.post(
                "https://otp.beem.africa/v1/verify", json=payload, headers=headers
            )
            data = response.json()

            if response.status_code == 200 and data.get("verified"):
                return VerifyOTP(verified=True, message="OTP verified successfully")
            else:
                return VerifyOTP(verified=False, message=data.get("message", "Verification failed"))
        except Exception as e:
            return VerifyOTP(verified=False, message=str(e))
