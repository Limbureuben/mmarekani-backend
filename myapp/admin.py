from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin

# # Register your models here.
# admin.site.register(CustomUser, UserAdmin)


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id', 'username', 'phone', 'national_id', 'is_staff')
admin.site.register(CustomUser, CustomUserAdmin)


class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'loan_amount', 'passport_picture', 'nida_front', 'submitted_at', 'status')
    list_filter = ('status', 'submitted_at')
    search_fields = ('user__username', 'user__phone')
admin.site.register(LoanApplication, LoanApplicationAdmin)