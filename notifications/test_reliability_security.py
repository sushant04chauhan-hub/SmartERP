from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Notification
from .services import (
    create_notification,
    create_notifications_for_roles,
)


class NotificationReliabilitySecurityTests(
    TestCase
):

    def setUp(self):

        User = get_user_model()

        self.user = User.objects.create_user(
            username="notification_security_user",
            password="test-password-123",
        )

        self.user.profile.role = (
            "INVENTORY"
        )
        self.user.profile.save()

        self.other_user = (
            User.objects.create_user(
                username="notification_other_user",
                password="test-password-123",
            )
        )

        self.notification = (
            create_notification(
                recipient=self.user,
                title="Security test notification",
                message=(
                    "Notification used for "
                    "reliability testing."
                ),
            )
        )

    def test_mark_read_is_idempotent(
        self,
    ):

        self.client.force_login(
            self.user
        )

        url = reverse(
            "api_notification_mark_read",
            args=[
                self.notification.id
            ],
        )

        first_response = (
            self.client.post(url)
        )

        self.assertEqual(
            first_response.status_code,
            200,
        )

        self.notification.refresh_from_db()

        first_read_at = (
            self.notification.read_at
        )

        second_response = (
            self.client.post(url)
        )

        self.assertEqual(
            second_response.status_code,
            200,
        )

        self.notification.refresh_from_db()

        self.assertTrue(
            self.notification.is_read
        )

        self.assertEqual(
            self.notification.read_at,
            first_read_at,
        )

    def test_mark_all_read_is_idempotent(
        self,
    ):

        create_notification(
            recipient=self.user,
            title="Second notification",
            message="Second notification.",
        )

        self.client.force_login(
            self.user
        )

        url = reverse(
            "api_notification_mark_all_read"
        )

        first_response = (
            self.client.post(url)
        )

        self.assertEqual(
            first_response.status_code,
            200,
        )

        self.assertEqual(
            first_response.json()[
                "updated_count"
            ],
            2,
        )

        second_response = (
            self.client.post(url)
        )

        self.assertEqual(
            second_response.status_code,
            200,
        )

        self.assertEqual(
            second_response.json()[
                "updated_count"
            ],
            0,
        )

    def test_mark_read_requires_post(
        self,
    ):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse(
                "api_notification_mark_read",
                args=[
                    self.notification.id
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )

        self.notification.refresh_from_db()

        self.assertFalse(
            self.notification.is_read
        )

    def test_mark_all_read_requires_post(
        self,
    ):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse(
                "api_notification_mark_all_read"
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_inactive_users_do_not_receive_role_notifications(
        self,
    ):

        self.user.is_active = False
        self.user.save(
            update_fields=[
                "is_active",
            ]
        )

        create_notifications_for_roles(
            roles={
                "INVENTORY",
            },
            title="Inventory alert",
            message="Test alert.",
        )

        self.assertEqual(
            Notification.objects.filter(
                recipient=self.user,
            ).count(),
            1,
        )

    def test_excluded_actor_does_not_receive_role_notification(
        self,
    ):

        create_notifications_for_roles(
            roles={
                "INVENTORY",
            },
            title="Inventory alert",
            message="Test alert.",
            exclude_user=self.user,
        )

        self.assertEqual(
            Notification.objects.filter(
                recipient=self.user,
            ).count(),
            1,
        )