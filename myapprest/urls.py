from .views import *
from django.urls import path
urlpatterns = [
    path('send/', send_otp),
    path('verify/', verify_otp),
]
