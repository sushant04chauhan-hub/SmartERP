from django.conf import settings
from django.db import models


class Notification(models.Model):

    TYPE_CHOICES = [
        ("INFO", "Information"),
        ("SUCCESS", "Success"),
        ("WARNING", "Warning"),
        ("ACTION_REQUIRED", "Action Required"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("NORMAL", "Normal"),
        ("HIGH", "High"),
        ("CRITICAL", "Critical"),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    notification_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default="INFO",
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="NORMAL",
    )

    title = models.CharField(
        max_length=200,
    )

    message = models.TextField()

    module = models.CharField(
        max_length=50,
        blank=True,
    )

    entity_type = models.CharField(
        max_length=100,
        blank=True,
    )

    entity_id = models.CharField(
        max_length=100,
        blank=True,
    )

    target_url = models.CharField(
        max_length=255,
        blank=True,
    )

    is_read = models.BooleanField(
        default=False,
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "-created_at",
            "-id",
        ]

        indexes = [
            models.Index(
                fields=[
                    "recipient",
                    "is_read",
                    "created_at",
                ],
                name="notif_rec_read_idx",
            ),
            models.Index(
                fields=[
                    "module",
                    "created_at",
                ],
                name="notif_module_idx",
            ),
        ]

    def __str__(self):

        return (
            f"{self.recipient.username} - "
            f"{self.title}"
        )