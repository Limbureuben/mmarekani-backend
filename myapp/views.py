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
import requests
from django.conf import settings
from .models import CustomUser
from graphene import Mutation, String, Boolean, Field
import base64



# Create your views here.
# class RegistrationMutation(graphene.Mutation):
#     user = graphene.Field(RegistrationObject)
#     output = graphene.Field(RegistrationResponse)

#     class Arguments:
#         input = RegistrationInputObject(required=True)

#     def mutate(self, info, input):
#         response = UserBuilder.register_user(input)
#         return RegistrationMutation(user=response.user, output=response)


# class UserType(DjangoObjectType):
#     class Meta:
#         model = CustomUser
#         fields = ("id", "username", "is_staff", "is_superuser")


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
            
            if not isinstance(user, CustomUser):
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




class RegistrationMutation(graphene.Mutation):
    user = graphene.Field(RegistrationResponse)
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        input = RegistrationInputObject(required=True)

    def mutate(self, info, input):
        if CustomUser.objects.filter(username=input.username).exists():
            return RegistrationMutation(success=False, message="Username already registered")
        # Validate if phone or national id already exists
        if CustomUser.objects.filter(phone=input.phone).exists():
            return RegistrationMutation(success=False, message="Phone number already registered")
        if CustomUser.objects.filter(national_id=input.national_id).exists():
            return RegistrationMutation(success=False, message="National ID already registered")

        # Create user without password (OTP login)
        user = CustomUser(
            username=input.username,  # or generate a unique username
            phone=input.phone,
            national_id=input.national_id,
        )
        user.set_unusable_password()  # no password, only OTP login
        user.save()

        return RegistrationMutation(
            user=user,
            success=True,
            message="User registered successfully"
        )



class OTPLoginMutation(Mutation):
    user = Field(UserLoginObject)
    success = Boolean()
    message = String()

    class Arguments:
        phone = String(required=True)
        pin_id = String(required=True)
        pin = String(required=True)

    def mutate(self, info, phone, pin_id, pin):
        try:
            # Verify OTP with Beem
            credentials = f"{settings.BEEM_APP_KEY}:{settings.BEEM_SECRET_KEY}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Basic {encoded_credentials}",
            }

            payload = {"pinId": pin_id, "pin": pin}
            res = requests.post("https://gateway.beem.africa/v1/otp/verify", json=payload, headers=headers)

            if res.status_code != 200 or not res.json().get("valid"):
                return OTPLoginMutation(success=False, message="Invalid OTP or verification failed.")

            # Lookup user
            try:
                user = CustomUser.objects.get(phone=phone)
            except CustomUser.DoesNotExist:
                return OTPLoginMutation(success=False, message="User not found. Please register.")

            # Generate token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            user_data = UserLoginObject(
                id=user.id,
                username=user.username,
                token=access_token,
                isStaff=user.is_staff,
            )

            return OTPLoginMutation(user=user_data, success=True, message="Login successful")

        except Exception as e:
            return OTPLoginMutation(success=False, message=f"Error: {str(e)}")




