from django.urls import path
from users.views import (
    ClientRegisterView,
    AdvocateRegisterView,
    LoginView,
    GoogleLoginView,
    ForgetPasswordView,
    ResetPasswordView,
    EnableMFAView,
    VerifyMFAView,
    ValidateTokenView,
)

urlpatterns = [

    # ---------------------- AUTH & REGISTER ----------------------
    path("register/client/", ClientRegisterView.as_view(), name="client-register"),
    path("register/advocate/", AdvocateRegisterView.as_view(), name="advocate-register"),

    path("login/", LoginView.as_view(), name="login"),
    path("login/google/", GoogleLoginView.as_view(), name="google-login"),

    # ---------------------- PASSWORD RESET -----------------------
    path("password/forgot/", ForgetPasswordView.as_view(), name="forget-password"),
    path("password/reset/", ResetPasswordView.as_view(), name="reset-password"),

    # ---------------------- MFA (TOTP) ---------------------------
    path("mfa/enable/", EnableMFAView.as_view(), name="enable-mfa"),
    path("mfa/verify/", VerifyMFAView.as_view(), name="verify-mfa"),

    # ---------------------- TOKEN VALIDATION ---------------------
    path("token/validate/", ValidateTokenView.as_view(), name="validate-token"),
]
