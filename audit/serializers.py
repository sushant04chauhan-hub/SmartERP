from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(
    serializers.ModelSerializer
):

    actor_username = serializers.CharField(
        source="actor.username",
        read_only=True,
    )

    class Meta:

        model = AuditLog

        fields = [
            "id",
            "actor",
            "actor_username",
            "action",
            "module",
            "entity_type",
            "entity_id",
            "entity_repr",
            "description",
            "metadata",
            "created_at",
        ]

        read_only_fields = fields