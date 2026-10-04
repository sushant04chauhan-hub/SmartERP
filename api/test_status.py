from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class ApiStatusTests(TestCase):

    def setUp(self):

        User = get_user_model()

        self.manager = (
            User.objects.create_user(
                username="status_manager",
                password="test-password-123",
            )
        )

        self.manager.profile.role = (
            "MANAGER"
        )
        self.manager.profile.save()

        self.finance_user = (
            User.objects.create_user(
                username="status_finance",
                password="test-password-123",
            )
        )

        self.finance_user.profile.role = (
            "FINANCE"
        )
        self.finance_user.profile.save()

    def test_status_requires_authentication(
        self,
    ):

        response = self.client.get(
            reverse("api_status")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_status_returns_user_context(
        self,
    ):

        self.client.force_login(
            self.manager
        )

        response = self.client.get(
            reverse("api_status")
        )

        data = response.json()

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            data["user"],
            "status_manager",
        )

        self.assertEqual(
            data["role"],
            "MANAGER",
        )

        self.assertFalse(
            data["is_superuser"]
        )

        self.assertTrue(
            data["can_view_audit_logs"]
        )

    def test_non_manager_cannot_view_audit_logs(
        self,
    ):

        self.client.force_login(
            self.finance_user
        )

        response = self.client.get(
            reverse("api_status")
        )

        self.assertFalse(
            response.json()[
                "can_view_audit_logs"
            ]
        )