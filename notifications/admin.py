from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(
    admin.ModelAdmin
):

    list_display = [
        "id",
        "recipient",
        "title",
        "notification_type",
        "priority",
        "is_read",
        "created_at",
    ]

    list_filter = [
        "notification_type",
        "priority",
        "is_read",
        "module",
        "created_at",
    ]

    search_fields = [
        "recipient__username",
        "title",
        "message",
        "entity_type",
        "entity_id",
    ]

    ordering = [
        "-created_at",
        "-id",
    ]

    readonly_fields = [
        "created_at",
        "read_at",
    ]