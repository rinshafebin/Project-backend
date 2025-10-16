from django.urls import path,include
from users.views import ClientRegisterView,LoginView,AdvocateRegisterView,ForgetPasswordView,ResetPasswordView

urlpatterns = [
    path('register/client/',ClientRegisterView.as_view(),name='client-register'),
    path('register/advocate/',AdvocateRegisterView.as_view(),name='advocate-register'),
    path('login/',LoginView.as_view(),name='login'),
    path('forget-password/',ForgetPasswordView.as_view(),name='forget-password'),
    path('reset-password/',ResetPasswordView.as_view(),name='reset-password'),

]
