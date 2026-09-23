from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(
    admin.ModelAdmin
):

    list_display = [
        "id",
        "created_at",
        "actor",
        "action",
        "module",
        "entity_type",
        "entity_id",
    ]

    list_filter = [
        "action",
        "module",
        "created_at",
    ]

    search_fields = [
        "actor__username",
        "entity_type",
        "entity_id",
        "entity_repr",
        "description",
    ]

    ordering = [
        "-created_at",
        "-id",
    ]

    readonly_fields = [
        "id",
        "actor",
        "action",
        "module",
        "entity_type",
        "entity_id",
        "entity_repr",
        "description",
        "metadata",
        "created_at",
    ]

    def has_add_permission(
        self,
        request,
    ):
        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return False