from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Notification
from .services import create_notification


class NotificationApiTests(TestCase):

    def setUp(self):

        User = get_user_model()

        self.user = User.objects.create_user(
            username="notification_user",
            password="test-password-123",
        )

        self.other_user = (
            User.objects.create_user(
                username="other_notification_user",
                password="test-password-123",
            )
        )

        self.notification = (
            create_notification(
                recipient=self.user,
                notification_type=(
                    "ACTION_REQUIRED"
                ),
                priority="HIGH",
                title="Expense requires review",
                message=(
                    "Expense AUD-001 "
                    "requires review."
                ),
                module="finance",
                entity_type="finance.Expense",
                entity_id="1",
                target_url="/finance",
            )
        )

        create_notification(
            recipient=self.other_user,
            title="Other user notification",
            message=(
                "This should not be visible "
                "to the first user."
            ),
        )

    def test_service_creates_unread_notification(
        self,
    ):

        self.assertFalse(
            self.notification.is_read
        )

        self.assertEqual(
            self.notification.priority,
            "HIGH",
        )

        self.assertEqual(
            self.notification.recipient,
            self.user,
        )

    def test_notification_api_requires_authentication(
        self,
    ):

        response = self.client.get(
            reverse(
                "api_notification_list"
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_user_only_sees_own_notifications(
        self,
    ):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse(
                "api_notification_list"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["count"],
            1,
        )

        self.assertEqual(
            data["results"][0]["title"],
            "Expense requires review",
        )

    def test_notification_list_is_paginated(
        self,
    ):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse(
                "api_notification_list"
            )
        )

        data = response.json()

        self.assertIn(
            "count",
            data,
        )

        self.assertIn(
            "results",
            data,
        )

    def test_notifications_can_be_searched(
        self,
    ):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse(
                "api_notification_list"
            ),
            {
                "search": "Expense",
            },
        )

        self.assertEqual(
            response.json()["count"],
            1,
        )

    def test_unread_count_is_correct(
        self,
    ):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse(
                "api_notification_unread_count"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json()[
                "unread_count"
            ],
            1,
        )

    def test_user_can_mark_notification_read(
        self,
    ):

        self.client.force_login(
            self.user
        )

        response = self.client.post(
            reverse(
                "api_notification_mark_read",
                args=[
                    self.notification.id
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.notification.refresh_from_db()

        self.assertTrue(
            self.notification.is_read
        )

        self.assertIsNotNone(
            self.notification.read_at
        )

    def test_user_cannot_mark_another_users_notification_read(
        self,
    ):

        other_notification = (
            Notification.objects.get(
                recipient=self.other_user
            )
        )

        self.client.force_login(
            self.user
        )

        response = self.client.post(
            reverse(
                "api_notification_mark_read",
                args=[
                    other_notification.id
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        other_notification.refresh_from_db()

        self.assertFalse(
            other_notification.is_read
        )

    def test_mark_all_read_only_updates_current_user(
        self,
    ):

        create_notification(
            recipient=self.user,
            title="Second notification",
            message="Second unread item.",
        )

        self.client.force_login(
            self.user
        )

        response = self.client.post(
            reverse(
                "api_notification_mark_all_read"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json()[
                "updated_count"
            ],
            2,
        )

        self.assertFalse(
            Notification.objects.filter(
                recipient=self.user,
                is_read=False,
            ).exists()
        )

        self.assertTrue(
            Notification.objects.filter(
                recipient=self.other_user,
                is_read=False,
            ).exists()
        )

    def test_notification_list_does_not_allow_post(
        self,
    ):

        self.client.force_login(
            self.user
        )

        response = self.client.post(
            reverse(
                "api_notification_list"
            ),
            {
                "title": "Invalid",
            },
        )

        self.assertEqual(
            response.status_code,
            405,
        )