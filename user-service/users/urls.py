from django.urls import path,include
from users.views import (
    ClientRegisterView,LoginView,
    AdvocateRegisterView,ForgetPasswordView,
    ResetPasswordView,VerifyMFAView,EnableMFAView,
    GoogleLoginView,
    AdvocateProfileView,
    ClientProfileView,
    ValidateTokenView
    )


urlpatterns = [
    
    path('client-register/',ClientRegisterView.as_view(),name='client-register'),
    path('advocate-register/',AdvocateRegisterView.as_view(),name='advocate-register'),
    path('login/',LoginView.as_view(),name='login'),
    path('google-login/', GoogleLoginView.as_view(), name='google-login'),
    path('forget-password/',ForgetPasswordView.as_view(),name='forget-password'),
    path('reset-password/',ResetPasswordView.as_view(),name='reset-password'),
    path('enable-mfa/', EnableMFAView.as_view()),
    path('verify-mfa/', VerifyMFAView.as_view()),
    path('advocate-profile/', AdvocateProfileView.as_view(), name='advocate-profile'),
    path('client-profile/', ClientProfileView.as_view(), name='client-profile'),
    path('validate-token/', ValidateTokenView.as_view(), name='validate-token'),

    
]

