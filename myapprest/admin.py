from django.contrib import admin
from .models import OTP

# Register your models here.
class OTPAdmin(admin.ModelAdmin):
    list_display = ('phone', 'code', 'created_at')
    list_filter = ('created_at',)
admin.site.register(OTP, OTPAdmin)
