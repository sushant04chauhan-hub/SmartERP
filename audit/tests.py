from django.contrib.auth import (
    get_user_model,
)
from django.test import TestCase
from django.urls import reverse

from .models import AuditLog
from .services import record_audit_log


class AuditLogTests(TestCase):

    def setUp(self):

        User = get_user_model()

        self.admin_user = (
            User.objects.create_user(
                username="audit_admin",
                password="test-password-123",
            )
        )

        self.admin_user.profile.role = (
            "ADMIN"
        )
        self.admin_user.profile.save()

        self.manager_user = (
            User.objects.create_user(
                username="audit_manager",
                password="test-password-123",
            )
        )

        self.manager_user.profile.role = (
            "MANAGER"
        )
        self.manager_user.profile.save()

        self.finance_user = (
            User.objects.create_user(
                username="audit_finance",
                password="test-password-123",
            )
        )

        self.finance_user.profile.role = (
            "FINANCE"
        )
        self.finance_user.profile.save()

        self.log = record_audit_log(
            user=self.admin_user,
            action="CREATE",
            module="inventory",
            entity_type="inventory.Product",
            entity_id="15",
            entity_repr="TEST001 - Test Product",
            description=(
                "Created test product."
            ),
            metadata={
                "product_code": "TEST001",
            },
        )

    def test_record_audit_log_creates_log(
        self,
    ):

        self.assertEqual(
            AuditLog.objects.count(),
            1,
        )

        self.assertEqual(
            self.log.actor,
            self.admin_user,
        )

        self.assertEqual(
            self.log.action,
            "CREATE",
        )

        self.assertEqual(
            self.log.module,
            "inventory",
        )

        self.assertEqual(
            self.log.entity_id,
            "15",
        )

    def test_audit_metadata_is_saved(
        self,
    ):

        self.assertEqual(
            self.log.metadata[
                "product_code"
            ],
            "TEST001",
        )

    def test_audit_api_requires_authentication(
        self,
    ):

        response = self.client.get(
            reverse("api_audit_logs")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_admin_can_view_audit_logs(
        self,
    ):

        self.client.force_login(
            self.admin_user
        )

        response = self.client.get(
            reverse("api_audit_logs")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json()["count"],
            1,
        )

    def test_manager_can_view_audit_logs(
        self,
    ):

        self.client.force_login(
            self.manager_user
        )

        response = self.client.get(
            reverse("api_audit_logs")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_other_roles_cannot_view_audit_logs(
        self,
    ):

        self.client.force_login(
            self.finance_user
        )

        response = self.client.get(
            reverse("api_audit_logs")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_audit_logs_can_be_searched(
        self,
    ):

        self.client.force_login(
            self.admin_user
        )

        response = self.client.get(
            reverse("api_audit_logs"),
            {
                "search": "TEST001",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json()["count"],
            1,
        )

    def test_audit_api_is_read_only(
        self,
    ):

        self.client.force_login(
            self.admin_user
        )

        response = self.client.post(
            reverse("api_audit_logs"),
            {
                "action": "DELETE",
            },
        )

        self.assertEqual(
            response.status_code,
            405,
        )