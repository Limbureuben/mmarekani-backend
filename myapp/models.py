from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# class CustomUser(AbstractUser):
#     username = models.CharField(max_length=100, unique=True)
#     phone = models.CharField(max_length=15, unique=True)
#     national_id = models.CharField(max_length=20, unique=True)
#     created_at = models.DateTimeField(default=timezone.now)

#     USERNAME_FIELD = 'phone'
#     REQUIRED_FIELDS = ['username']

#     def __str__(self):
#         return self.phone


from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=15, unique=True)
    national_id = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username', 'national_id']

    def __str__(self):
        return self.phone


class OTP(models.Model):
    phone = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone} - {self.code}"



class LoanApplication(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loan_applications')
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    passport_picture = models.ImageField(upload_to='loan_documents/passport_pictures/')
    nida_front = models.ImageField(upload_to='loan_documents/nida_pictures/front/', null=True, blank=True)
    nida_back = models.ImageField(upload_to='loan_documents/nida_pictures/back/', null=True, blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, default='pending')  # pending, approved, rejected

    def __str__(self):
        return f"Loan Application by {self.user.username} for {self.loan_amount}"
