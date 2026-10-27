
import json
from datetime import timedelta
from django.test import override_settings
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.hashers import make_password

from .models import User
from .jwtutils import create_access_token
from unittest.mock import patch
from django.db import IntegrityError, transaction


class EMSystemAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password=make_password("TestPass123!"),
            valid_until=timezone.now() + timedelta(days=100),
        )

        self.token = create_access_token(self.user)
        self.auth_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.token}"
        }

    def test_home_endpoint(self):
        response = self.client.get("/api/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["status"],
            "success",
        )

    def test_login_success(self):
        response = self.client.post(
            "/api/login",
            data=json.dumps({
                "email": "test@example.com",
                "password": "TestPass123!",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())

    def test_login_invalid_password(self):
        response = self.client.post(
            "/api/login",
            data=json.dumps({
                "email": "test@example.com",
                "password": "WrongPassword123!",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)

    def test_profile_requires_token(self):
        response = self.client.get("/api/me")

        self.assertEqual(response.status_code, 401)

    def test_profile_with_valid_token(self):
        response = self.client.get(
            "/api/me",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["account_valid"])

    def test_user_list_does_not_expose_password(self):
        response = self.client.get(
            "/api/user-list",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 200)

        users = response.json()["users"]
        self.assertEqual(len(users), 1)
        self.assertNotIn("password", users[0])

    def test_patch_updates_user(self):
        response = self.client.patch(
            f"/api/update/{self.user.user_id}",
            data=json.dumps({
                "first_name": "Updated",
            }),
            content_type="application/json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")

    def test_expired_account_is_rejected(self):
        self.user.valid_until = timezone.now() - timedelta(days=1)
        self.user.save(update_fields=["valid_until"])

        response = self.client.get(
            "/api/me",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["code"],
            "account_expired",
        )

    
    def test_registration_success(self):
        response = self.client.post(
            "/api/register",
            data=json.dumps({
                "first_name": "New",
                "last_name": "Employee",
                "email": "new@example.com",
                "password": "SecurePass123!",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertNotIn("password", response.json()["user"])

    def test_registration_duplicate_email(self):
        response = self.client.post(
            "/api/register",
            data=json.dumps({
                "first_name": "Duplicate",
                "last_name": "User",
                "email": self.user.email.upper(),
                "password": "SecurePass123!",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 409)

    def test_registration_rejects_short_password(self):
        response = self.client.post(
            "/api/register",
            data=json.dumps({
                "first_name": "New",
                "last_name": "Employee",
                "email": "shortpass@example.com",
                "password": "123",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_user_creation_requires_token(self):
        response = self.client.post(
            "/api/user-create",
            data=json.dumps({
                "first_name": "New",
                "last_name": "Employee",
                "email": "created@example.com",
                "password": "SecurePass123!",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)

    def test_user_creation_success(self):
        response = self.client.post(
            "/api/user-create",
            data=json.dumps({
                "first_name": "New",
                "last_name": "Employee",
                "email": "created@example.com",
                "password": "SecurePass123!",
            }),
            content_type="application/json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 201)
        self.assertNotIn("password", response.json()["user"])

        created_user = User.objects.get(
            email="created@example.com"
        )
        self.assertNotEqual(
            created_user.password,
            "SecurePass123!",
        )

    def test_put_updates_all_profile_fields(self):
        response = self.client.put(
            f"/api/update/{self.user.user_id}",
            data=json.dumps({
                "first_name": "Updated",
                "last_name": "Employee",
                "email": "updated@example.com",
            }),
            content_type="application/json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "Employee")
        self.assertEqual(self.user.email, "updated@example.com")

    def test_delete_user_success(self):
        response = self.client.delete(
            f"/api/delete/{self.user.user_id}",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(
                user_id=self.user.user_id
            ).exists()
        )

    def test_invalid_jwt_is_rejected(self):
        response = self.client.get(
            "/api/me",
            HTTP_AUTHORIZATION="Bearer invalid.token.value",
        )

        self.assertEqual(response.status_code, 401)

    def test_pagination_rejects_oversized_page_size(self):
        response = self.client.get(
            "/api/user-list?page=1&page_size=500",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 400)

    
    def test_registration_rejects_missing_fields(self):
        response = self.client.post(
            "/api/register",
            data=json.dumps({
                "email": "missing@example.com",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_registration_rejects_invalid_email(self):
        response = self.client.post(
            "/api/register",
            data=json.dumps({
                "first_name": "New",
                "last_name": "Employee",
                "email": "not-an-email",
                "password": "SecurePass123!",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_user_creation_rejects_duplicate_email(self):
        response = self.client.post(
            "/api/user-create",
            data=json.dumps({
                "first_name": "Another",
                "last_name": "User",
                "email": self.user.email.upper(),
                "password": "SecurePass123!",
            }),
            content_type="application/json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(User.objects.count(), 1)

    def test_update_rejects_duplicate_email(self):
        other_user = User.objects.create(
            first_name="Other",
            last_name="Employee",
            email="other@example.com",
            password=make_password("OtherPass123!"),
            valid_until=timezone.now() + timedelta(days=100),
        )

        original_email = self.user.email

        response = self.client.patch(
            f"/api/update/{self.user.user_id}",
            data=json.dumps({
                "email": other_user.email,
            }),
            content_type="application/json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 409)

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, original_email)

    def test_delete_nonexistent_user_returns_404(self):
        nonexistent_id = self.user.user_id + 999999

        response = self.client.delete(
            f"/api/delete/{nonexistent_id}",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 404)

    def test_pagination_rejects_invalid_values(self):
        invalid_queries = [
            "page=0",
            "page=-1",
            "page_size=0",
            "page_size=-1",
            "page=abc",
            "page_size=abc",
        ]

        for query in invalid_queries:
            with self.subTest(query=query):
                response = self.client.get(
                    f"/api/user-list?{query}",
                    **self.auth_headers,
                )

                self.assertEqual(response.status_code, 400)

    def test_profile_update_does_not_change_password_hash(self):
        original_hash = self.user.password

        response = self.client.patch(
            f"/api/update/{self.user.user_id}",
            data=json.dumps({
                "first_name": "Password",
                "last_name": "SafetyCheck",
            }),
            content_type="application/json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertEqual(self.user.password, original_hash)
        self.assertNotEqual(
            self.user.password,
            "TestPass123!",
        )

    
    def test_duplicate_email_database_constraint_rolls_back(self):
        # The existing test user already owns this email.
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create(
                    first_name="Duplicate",
                    last_name="Employee",
                    email=self.user.email,
                    password=make_password("SecurePass123!"),
                    valid_until=timezone.now() + timedelta(days=100),
                )

        # The failed insert must not create another user.
        self.assertEqual(User.objects.count(), 1)

    @patch(
        "userauth.views.User.objects.create",
        side_effect=IntegrityError("Simulated database constraint error"),
    )
    def test_registration_handles_database_integrity_error(self, mock_create):
        response = self.client.post(
            "/api/register",
            data=json.dumps({
                "first_name": "New",
                "last_name": "Employee",
                "email": "new-atomic@example.com",
                "password": "SecurePass123!",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(User.objects.count(), 1)
        mock_create.assert_called_once()


    @override_settings(PASSWORD_RESET_DEMO_ENABLED=True)
    def test_password_reset_success(self):
        response = self.client.post(
            "/api/password-reset",
            data=json.dumps({
                "email": "test@example.com",
                "new_password": "NewPass456!",
                "confirm_password": "NewPass456!",
            }),
            content_type="application/json",
        )
        print("RESET RESPONSE:", response.status_code, response.json())
        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()

        # The database must store a hash, not plain-text password.
        self.assertNotEqual(self.user.password, "NewPass456!")

        # The new password works.
        self.assertTrue(
            self.user.password.startswith("pbkdf2_")
            or self.user.password.startswith("argon2")
            or self.user.password.startswith("bcrypt")
        )

        # The old password no longer works.
        from django.contrib.auth.hashers import check_password

        self.assertFalse(
            check_password("TestPass123!", self.user.password)
        )
        self.assertTrue(
            check_password("NewPass456!", self.user.password)
        )

    @override_settings(PASSWORD_RESET_DEMO_ENABLED=True)
    def test_password_reset_rejects_mismatched_passwords(self):
        response = self.client.post(
            "/api/password-reset",
            data=json.dumps({
                "email": "test@example.com",
                "new_password": "NewPass456!",
                "confirm_password": "DifferentPass789!",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

        self.user.refresh_from_db()
        from django.contrib.auth.hashers import check_password

        self.assertTrue(
            check_password("TestPass123!", self.user.password)
        )

    @override_settings(PASSWORD_RESET_DEMO_ENABLED=True)
    def test_password_reset_rejects_short_password(self):
        response = self.client.post(
            "/api/password-reset",
            data=json.dumps({
                "email": "test@example.com",
                "new_password": "123",
                "confirm_password": "123",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        
    @override_settings(PASSWORD_RESET_DEMO_ENABLED=True)
    def test_password_reset_rejects_unknown_email(self):
        response = self.client.post(
            "/api/password-reset",
            data=json.dumps({
                "email": "unknown@example.com",
                "new_password": "NewPass456!",
                "confirm_password": "NewPass456!",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)

    @override_settings(PASSWORD_RESET_DEMO_ENABLED=True)
    def test_password_reset_rejects_get_request(self):
        response = self.client.get("/api/password-reset")

        self.assertEqual(response.status_code, 405)
