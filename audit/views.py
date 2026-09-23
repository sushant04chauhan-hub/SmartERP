from rest_framework import filters
from rest_framework.generics import ListAPIView
from rest_framework.permissions import BasePermission

from api.pagination import StandardResultsSetPagination

from .models import AuditLog
from .serializers import AuditLogSerializer


class CanViewAuditLogs(BasePermission):

    message = (
        "Only administrators and managers "
        "can view audit logs."
    )

    def has_permission(
        self,
        request,
        view,
    ):

        user = request.user

        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        profile = getattr(
            user,
            "profile",
            None,
        )

        if profile is None:
            return False

        return profile.role in {
            "ADMIN",
            "MANAGER",
        }


class AuditLogListAPIView(ListAPIView):

    serializer_class = AuditLogSerializer

    permission_classes = [
        CanViewAuditLogs
    ]

    pagination_class = (
        StandardResultsSetPagination
    )

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "actor__username",
        "action",
        "module",
        "entity_type",
        "entity_id",
        "entity_repr",
        "description",
    ]

    ordering_fields = [
        "created_at",
        "action",
        "module",
        "entity_type",
        "actor__username",
    ]

    ordering = [
        "-created_at",
        "-id",
    ]

    def get_queryset(self):

        return (
            AuditLog.objects
            .select_related("actor")
            .all()
        )