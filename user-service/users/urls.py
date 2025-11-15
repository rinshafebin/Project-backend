from django.urls import path
from users.views import (
    UserRegisterView,
    AdvocateRegisterView,
    LoginView,
    GoogleLoginView,
    EnableMFAView,
    VerifyMFAView,
    ClientProfileUpdateView,
    AdvocateProfileUpdateView
)

urlpatterns = [
    path('register/user/', UserRegisterView.as_view(), name='user-register'),
    path('register/advocate/', AdvocateRegisterView.as_view(), name='advocate-register'),
    path('login/', LoginView.as_view(), name='login'),
    path('login/google/', GoogleLoginView.as_view(), name='google-login'),
    path('mfa/enable/', EnableMFAView.as_view(), name='enable-mfa'),
    path('mfa/verify/', VerifyMFAView.as_view(), name='verify-mfa'),
    path('profile/client/', ClientProfileUpdateView.as_view(), name='client-profile-update'),
    path('profile/advocate/', AdvocateProfileUpdateView.as_view(), name='advocate-profile-update'),
]
