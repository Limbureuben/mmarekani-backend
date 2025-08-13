from rest_framework import serializers # type: ignore
from .models import *
from django.contrib.auth import get_user_model

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
        fields = ['loan_amount', 'passport_picture', 'nida_front', 'nida_back']

    def create(self, validated_data):
        # Attach the logged-in user automatically
        request = self.context.get('request')
        user = request.user if request else None
        return LoanApplication.objects.create(user=user, **validated_data)

class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'phone', 'national_id']

class LoanApplicationSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = LoanApplication
        fields = [
            'id',
            'user',
            'loan_amount',
            'passport_picture',
            'nida_front',
            'nida_back',
            'submitted_at',
            'status',
        ]
        
        
class UserProfileStatsSerializer(serializers.Serializer):
    username = serializers.CharField()
    phone = serializers.CharField()
    national_id = serializers.CharField()
    total_applications = serializers.IntegerField()
    total_approved = serializers.IntegerField()
    total_rejected = serializers.IntegerField()
    money_approved = serializers.DecimalField(max_digits=12, decimal_places=2)
    money_pending = serializers.DecimalField(max_digits=12, decimal_places=2)
    money_rejected = serializers.DecimalField(max_digits=12, decimal_places=2)


class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    receiver_username = serializers.CharField(source='receiver.username', read_only=True)
    class Meta:
        model = Notification
        fields = ['id', 'sender', 'sender_username', 'receiver', 'receiver_username', 'message', 'created_at', 'is_read']
        read_only_fields = ['id', 'created_at', 'sender_username', 'receiver_username']


class LoanStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['accepted', 'rejected'])


class LoanReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanReceipt
        fields = ['id', 'receipt_image', 'uploaded_at', 'username', 'phone']