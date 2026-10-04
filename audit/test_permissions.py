from django.contrib.auth import (
    get_user_model,
)
from django.test import TestCase
from django.urls import reverse


class AuditPermissionTests(TestCase):

    def test_superuser_can_access_audit_api(
        self,
    ):

        User = get_user_model()

        superuser = (
            User.objects.create_superuser(
                username="audit_superuser",
                email="audit@example.com",
                password="test-password-123",
            )
        )

        self.client.force_login(
            superuser
        )

        response = self.client.get(
            reverse(
                "api_audit_logs"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )