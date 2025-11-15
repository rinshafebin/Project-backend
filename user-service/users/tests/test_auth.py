from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthAPITests(APITestCase):

    def setUp(self):
        self.client_user = User.objects.create_user(
            email="client@gmail.com",
            password="ClientPass123!",
            username="clientuser",
            role="client"
        )

        self.advocate_user = User.objects.create_user(
            email="advocate@gmail.com",
            password="AdvocatePass123!",
            username="advocateuser",
            role="advocate"
        )

    def assertStatus(self, response, expected_status):
        if response.status_code != expected_status:
            self.fail(
                f"\nExpected: {expected_status}\n"
                f"Got: {response.status_code}\n"
                f"Response Data: {response.data}\n"
            )

    # --------------------------- REGISTER TESTS ---------------------------

    @patch("users.views.send_welcome_email.delay")
    @patch("users.views.emit_user_created_event")
    def test_client_register(self, mock_event, mock_welcome):
        url = reverse("client-register")
        data = {
            "username": "newclientuser",
            "email": "newclient@gmail.com",
            "password": "NewClientPass123!",
            "confirm_password": "NewClientPass123!",
            "role": "client",   
        }

        response = self.client.post(url, data, format="json")
        self.assertStatus(response, status.HTTP_201_CREATED)

    @patch("users.views.send_welcome_email.delay")
    @patch("users.views.emit_user_created_event")
    def test_advocate_register(self, mock_event, mock_welcome):
        url = reverse("advocate-register")
        data = {
            "username": "newadvocateuser",
            "email": "newadvocate@gmail.com",
            "password": "NewAdvocatePass123!",
            "confirm_password": "NewAdvocatePass123!",
            "role": "advocate",            # REQUIRED
            "phone_number": "9998887776",  # REQUIRED
            "bar_council_number": "BAR1234",  # REQUIRED
        }

        response = self.client.post(url, data, format="json")
        self.assertStatus(response, status.HTTP_201_CREATED)

    # --------------------------- LOGIN TESTS ---------------------------

    def test_login_success(self):
        url = reverse("login")
        data = {
            "email": "client@gmail.com",
            "password": "ClientPass123!"
        }
        response = self.client.post(url, data, format="json")
        self.assertStatus(response, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_wrong_password(self):
        url = reverse("login")
        data = {
            "email": "client@gmail.com",
            "password": "WrongPass12!"
        }
        response = self.client.post(url, data, format="json")
        self.assertStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    # ---------------------- FORGET / RESET PASSWORD ----------------------

    @patch("django.core.mail.send_mail")
    def test_forgot_password(self, mock_mail):
        url = reverse("forget-password")
        data = {"email": "client@gmail.com"}
        response = self.client.post(url, data, format="json")
        self.assertStatus(response, status.HTTP_200_OK)

        # OTP stored?
        from users import views as user_views
        self.assertIn("client@gmail.com", user_views.otp_storage)

    def test_reset_password(self):
        # 1. Generate OTP
        with patch("django.core.mail.send_mail"):
            self.client.post(reverse("forget-password"), {"email": "client@gmail.com"}, format="json")

        # 2. Retrieve OTP
        from users import views as user_views
        otp = user_views.otp_storage.get("client@gmail.com")
        self.assertIsNotNone(otp)

        # 3. Reset password
        url = reverse("reset-password")
        data = {
            "email": "client@gmail.com",
            "otp": otp,
            "new_password": "ResetPass123!",
        }

        response = self.client.post(url, data, format="json")
        self.assertStatus(response, status.HTTP_200_OK)

        # 4. Login with new password
        login = self.client.post(
            reverse("login"),
            {"email": "client@gmail.com", "password": "ResetPass123!"},
            format="json",
        )
        self.assertStatus(login, status.HTTP_200_OK)
