import random
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework import status, permissions # type: ignore
from .models import CustomUser, OTP
from .serializers import *
from django.utils import timezone
from datetime import timedelta
from .beem_otp import send_otp_via_beem
from django.db.models import Q
import base64
import requests
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from django.db.models import Sum
from django.shortcuts import get_object_or_404

class RegisterUserView(APIView):
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Registered successfully, proceed to login'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginWithPhoneView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')

        if not phone or not password:
            return Response({'error': 'Phone and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(phone=phone)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid phone or password'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({'error': 'Invalid phone or password'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'phone': user.phone,
            }
        }, status=status.HTTP_200_OK)



class LoanApplicationCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        serializer = LoanApplicationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)  # No need to pass user here
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AdminLoanApplicationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        loan_apps = LoanApplication.objects.all().order_by('-submitted_at')
        serializer = LoanApplicationSerializer(loan_apps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# User view - only user's own loan applications
# class UserLoanApplicationsView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         loan_apps = LoanApplication.objects.filter(user=request.user, status='pending').order_by('-submitted_at')
#         serializer = LoanApplicationSerializer(loan_apps, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


class UserLoanApplicationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        loan_apps = LoanApplication.objects.filter(user=request.user).order_by('-submitted_at')
        serializer = LoanApplicationSerializer(loan_apps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        print(f"Request User: {user} (id: {user.id})")

        user_loans = LoanApplication.objects.filter(user=user)

        print(f"Loans found: {user_loans.count()}")

        total_applications = user_loans.count()
        total_approved = user_loans.filter(status='accepted').count()
        total_rejected = user_loans.filter(status='rejected').count()

        money_approved = user_loans.filter(status='accepted').aggregate(total=Sum('loan_amount'))['total'] or 0
        money_pending = user_loans.filter(status='pending').aggregate(total=Sum('loan_amount'))['total'] or 0
        money_rejected = user_loans.filter(status='rejected').aggregate(total=Sum('loan_amount'))['total'] or 0

        profile_data = {
            "username": user.username,
            "phone": user.phone,
            "national_id": user.national_id,
            "total_applications": total_applications,
            "total_approved": total_approved,
            "total_rejected": total_rejected,
            "money_approved": money_approved,
            "money_pending": money_pending,
            "money_rejected": money_rejected,
        }
        print("Profile data to return:", profile_data)

        serializer = UserProfileStatsSerializer(profile_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


User = get_user_model()
class NotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def _get_queryset(self, user):
        if user.is_staff:
            # Admin sees notifications not marked deleted on receiver side
            return Notification.objects.filter(receiver_deleted=False).order_by('created_at')
        else:
            # Users see only notifications not deleted on their side
            return Notification.objects.filter(
                (Q(sender=user) & Q(sender_deleted=False)) |
                (Q(receiver=user) & Q(receiver_deleted=False))
            ).order_by('created_at')

    # def get(self, request):
    #     user = request.user
    #     if user.is_staff:
    #         # Admin can see all notifications
    #         notifications = Notification.objects.all().order_by('created_at')
    #     else:
    #         # User sees only messages sent or received by them (mostly their own sent messages and replies by admin)
    #         notifications = Notification.objects.filter(sender=user) | Notification.objects.filter(receiver=user)
    #         notifications = notifications.order_by('created_at')
    #     serializer = NotificationSerializer(notifications, many=True)
    #     return Response(serializer.data)
    
    
    def get(self, request):
        user = request.user
        notifications = self._get_queryset(user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    
    
    def post(self, request):
        user = request.user
        data = request.data

        message = data.get('message', '').strip()
        if not message:
            return Response({"detail": "Message cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_staff:
            receiver_id = data.get('receiver')
            if not receiver_id:
                return Response({"detail": "Receiver is required for admin messages."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                receiver = User.objects.get(id=receiver_id, is_staff=False)
            except User.DoesNotExist:
                return Response({"detail": "Receiver user not found or is not a regular user."}, status=status.HTTP_400_BAD_REQUEST)
            notification = Notification.objects.create(sender=user, receiver=receiver, message=message)
            serializer = NotificationSerializer(notification)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            admin_user = User.objects.filter(is_staff=True).first()
            if not admin_user:
                return Response({"detail": "No admin available to receive messages."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            notification = Notification.objects.create(sender=user, receiver=admin_user, message=message)
            serializer = NotificationSerializer(notification)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        user = request.user
        notification = get_object_or_404(Notification, pk=pk)

        # Only sender or receiver or admin can soft delete the notification on their side
        if notification.sender != user and notification.receiver != user and not user.is_staff:
            return Response({"detail": "You do not have permission to delete this notification."},
                            status=status.HTTP_403_FORBIDDEN)

        # Mark deletion flag for the user or both if admin
        if notification.sender == user:
            notification.sender_deleted = True
        elif notification.receiver == user:
            notification.receiver_deleted = True
        elif user.is_staff:
            # Optionally, admin can delete both sides at once
            notification.sender_deleted = True
            notification.receiver_deleted = True

        notification.save()

        # If both sides deleted, remove record permanently
        if notification.sender_deleted and notification.receiver_deleted:
            notification.delete()

        return Response({"detail": "Notification deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


    # def post(self, request):
    #     user = request.user
    #     data = request.data

    #     # Validate message content
    #     message = data.get('message', '').strip()
    #     if not message:
    #         return Response({"detail": "Message cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

    #     # Admin sending a message (must specify receiver user id)
    #     if user.is_staff:
    #         receiver_id = data.get('receiver')
    #         if not receiver_id:
    #             return Response({"detail": "Receiver is required for admin messages."}, status=status.HTTP_400_BAD_REQUEST)
    #         try:
    #             receiver = User.objects.get(id=receiver_id, is_staff=False)  # Receiver must be a normal user
    #         except User.DoesNotExist:
    #             return Response({"detail": "Receiver user not found or is not a regular user."}, status=status.HTTP_400_BAD_REQUEST)
    #         # Create message from admin to user
    #         notification = Notification.objects.create(sender=user, receiver=receiver, message=message)
    #         serializer = NotificationSerializer(notification)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)

    #     else:
    #         # User sending a message (receiver is always admin)
    #         try:
    #             admin_user = User.objects.filter(is_staff=True).first()
    #         except User.DoesNotExist:
    #             return Response({"detail": "Admin user not found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #         if not admin_user:
    #             return Response({"detail": "No admin available to receive messages."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #         # Create message from user to admin
    #         notification = Notification.objects.create(sender=user, receiver=admin_user, message=message)
    #         serializer = NotificationSerializer(notification)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        
    def delete(self, request, pk):
        user = request.user
        notification = get_object_or_404(Notification, pk=pk)

        # Allow deletion only if the user is sender OR admin (if you want admins to delete any)
        if notification.sender != user and not user.is_staff:
            return Response({"detail": "You do not have permission to delete this notification."},
                            status=status.HTTP_403_FORBIDDEN)

        notification.delete()
        return Response({"detail": "Notification deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class LoanApplicationStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        # Only allow admin users
        if not request.user.is_staff:
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)

        loan = get_object_or_404(LoanApplication, pk=pk)
        serializer = LoanStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            loan.status = serializer.validated_data['status']
            loan.save()
            return Response(
                {"detail": f"Loan application status updated to {loan.status}."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoanApplicationDeleteView(APIView):
    permission_classes = [permissions.IsAdminUser]  # Only admins allowed

    def delete(self, request, pk):
        loan = get_object_or_404(LoanApplication, pk=pk)
        loan.delete()
        return Response({"detail": "Loan application deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class LoanApplicationStatsView(APIView):
    permission_classes = [permissions.IsAdminUser]  # Only admins can access

    def get(self, request):
        total = LoanApplication.objects.count()
        total_accepted = LoanApplication.objects.filter(status='accepted').count()
        total_pending = LoanApplication.objects.filter(status='pending').count()
        total_rejected = LoanApplication.objects.filter(status='rejected').count()

        data = {
            "total_applications": total,
            "total_accepted": total_accepted,
            "total_pending": total_pending,
            "total_rejected": total_rejected,
        }
        return Response(data)



# class LoanReceiptUploadView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, pk):
#         loan_application = get_object_or_404(LoanApplication, pk=pk, user=request.user)

#         data = request.data.copy()
#         data['loan_application'] = loan_application.id
#         # Set username and phone_number from logged-in user info
#         data['username'] = request.user.username
        
#         # Assuming phone number is stored in user profile or user model field called 'phone_number'
#         phone_number = getattr(request.user, 'phone_number', None)
#         if not phone_number:
#             return Response({'error': 'User phone number not found'}, status=status.HTTP_400_BAD_REQUEST)
#         data['phone_number'] = phone_number

#         serializer = LoanReceiptSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'message': 'Receipt uploaded successfully'}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoanReceiptUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        data['username'] = request.user.username
        phone = getattr(request.user, 'phone', None)
        if not phone:
            return Response({'error': 'User phone number not found'}, status=status.HTTP_400_BAD_REQUEST)
        data['phone'] = phone
        
        serializer = LoanReceiptSerializer(data=data)
        if serializer.is_valid():
            receipt = serializer.save()
            receipt_url = request.build_absolute_uri(receipt.receipt_image.url)  # Full URL
            
            return Response({
                'message': 'Receipt uploaded successfully',
                'receipt_url': receipt_url
            }, status=status.HTTP_201_CREATED)
        
        # Return serializer errors for debugging
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": "Account deleted successfully"}, status=status.HTTP_204_NO_CONTENT)



class LoanReceiptListView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Require token

    def get(self, request):
        receipts = LoanReceipt.objects.all().order_by('-uploaded_at')
        serializer = LoanReceiptSerializer(receipts, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class LoanReceiptDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            receipt = LoanReceipt.objects.get(pk=pk)
            receipt.delete()
            return Response({"message": "Receipt deleted"}, status=status.HTTP_204_NO_CONTENT)
        except LoanReceipt.DoesNotExist:
            return Response({"error": "Receipt not found"}, status=status.HTTP_404_NOT_FOUND)














class SendOTPView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        print("Received phone:", phone)

        if not phone:
            return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

        phone = phone.lstrip("+")

        url = "https://apiotp.beem.africa/v1/request"
        auth_string = f"{settings.BEEM_API_KEY}:{settings.BEEM_SECRET_KEY}"
        print("Auth string (plain):", repr(auth_string))  # Show raw string, check for extra spaces or newlines

        auth_header = base64.b64encode(auth_string.encode()).decode()
        print("Auth header (base64):", auth_header)  # This is what is sent as Basic auth header

        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json",
        }

        payload = {
            "appId": settings.BEEM_APP_ID,
            "msisdn": phone,
            "channel": "sms"
        }

        try:
            response = requests.post(url, json=payload, headers=headers, verify=False)
            print("Beem response:", response.status_code, response.text)
            response.raise_for_status()
            return Response(response.json(), status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            print("Exception:", e)
            return Response({"error": f"Error sending OTP: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            code = serializer.validated_data['code']

            try:
                otp = OTP.objects.filter(phone=phone, code=code).latest('created_at')
            except OTP.DoesNotExist:
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

            if timezone.now() - otp.created_at > timedelta(minutes=5):
                return Response({'error': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)

            user = CustomUser.objects.get(phone=phone)

            OTP.objects.filter(phone=phone).delete()

            return Response({'message': 'OTP verified successfully', 'username': user.username}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
