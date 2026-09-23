from rest_framework import serializers

from .models import Notification


class NotificationSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Notification

        fields = [
            "id",
            "notification_type",
            "priority",
            "title",
            "message",
            "module",
            "entity_type",
            "entity_id",
            "target_url",
            "is_read",
            "read_at",
            "created_at",
        ]

        read_only_fields = fields