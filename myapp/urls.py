from .views import *
from django.urls import path

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginWithPhoneView.as_view(), name='login-with-phone'),
    path('apply-loan/', LoanApplicationCreateView.as_view(), name='apply-loan'),
    path('admin/loan-applications/', AdminLoanApplicationsView.as_view(), name='admin-loan-applications'),
    path('user/loan-applications/', UserLoanApplicationsView.as_view(), name='user-loan-applications'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('notifications/', NotificationView.as_view(), name='notifications'),
    path('notifications/<int:pk>/', NotificationView.as_view(), name='notification-detail'),
    path('loan-applications/<int:pk>/status/', LoanApplicationStatusUpdateView.as_view(), name='loan-application-status-update'),
    path('admin/loan-applications/<int:pk>/status/', LoanApplicationStatusUpdateView.as_view(), name='loan-status-update'),
    path('admin/loan-applications/<int:pk>/delete/', LoanApplicationDeleteView.as_view(), name='loan-application-delete'),
    path('loan-applications/stats/', LoanApplicationStatsView.as_view(), name='loan-application-stats'),
    # path('loan-applications/', LoanApplicationListAPIView.as_view(), name='loan-applications'),
    path('send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
]
