from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, unique=True)
    national_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.username} ({self.phone})"