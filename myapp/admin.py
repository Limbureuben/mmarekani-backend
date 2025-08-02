from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin

# # Register your models here.
# admin.site.register(CustomUser, UserAdmin)


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id', 'username', 'phone', 'national_id', 'is_staff')

admin.site.register(CustomUser, CustomUserAdmin)
