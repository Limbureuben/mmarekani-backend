from tokenize import TokenError
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from graphql import GraphQLError
from commerce_dto.Response import *
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from myapp.models import CustomUser



class UserBuilder:
    def register_user(input):
        if input.password != input.passwordConfirm:
            raise ValidationError("Passwords do not match")

        if CustomUser.objects.filter(username=input.username).exists():
            raise ValidationError("Username already exists")

        if input.email and CustomUser.objects.filter(email=input.email).exists():
            raise ValidationError("Email already exists")

        user = CustomUser.objects.create_user(
            username=input.username,
            email=input.email or "",
            password=input.password,
        )

        user_data = RegistrationObject(
            id=user.id,
            username=user.username,
            email=user.email
        )

        response = RegistrationResponse(success=True, message="User registered successfully")
        return response
        
    
    
    
    
    
    
    
    
    
    
