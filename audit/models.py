from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class AuditLog(models.Model):

    ACTION_CHOICES = [
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        ("APPROVE", "Approve"),
        ("REJECT", "Reject"),
        ("CONFIRM", "Confirm"),
        ("ORDER", "Order"),
        ("RECEIVE", "Receive"),
        ("COMPLETE", "Complete"),
        ("CANCEL", "Cancel"),
        ("PAY", "Pay"),
        ("STOCK_IN", "Stock In"),
        ("STOCK_OUT", "Stock Out"),
        ("ADJUST", "Adjust"),
    ]

    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES,
    )

    module = models.CharField(
        max_length=50,
    )

    entity_type = models.CharField(
        max_length=100,
    )

    entity_id = models.CharField(
        max_length=100,
        blank=True,
    )

    entity_repr = models.CharField(
        max_length=255,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    metadata = models.JSONField(
        default=dict,
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
                fields=["created_at"],
                name="audit_created_idx",
            ),
            models.Index(
                fields=[
                    "module",
                    "action",
                ],
                name="audit_module_action_idx",
            ),
            models.Index(
                fields=[
                    "entity_type",
                    "entity_id",
                ],
                name="audit_entity_idx",
            ),
        ]

    def __str__(self):

        actor_name = (
            self.actor.username
            if self.actor
            else "System"
        )

        return (
            f"{actor_name} - "
            f"{self.action} - "
            f"{self.entity_type} "
            f"{self.entity_id}"
        )