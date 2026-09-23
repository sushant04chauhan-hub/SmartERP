from django.shortcuts import get_object_or_404

from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from api.pagination import StandardResultsSetPagination

from .models import Notification
from .serializers import NotificationSerializer
from .services import (
    mark_all_notifications_read,
    mark_notification_read,
)


class NotificationListAPIView(
    ListAPIView
):

    serializer_class = NotificationSerializer

    permission_classes = [
        IsAuthenticated
    ]

    pagination_class = (
        StandardResultsSetPagination
    )

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "title",
        "message",
        "notification_type",
        "priority",
        "module",
        "entity_type",
        "entity_id",
    ]

    ordering_fields = [
        "created_at",
        "priority",
        "notification_type",
        "is_read",
    ]

    ordering = [
        "-created_at",
        "-id",
    ]

    def get_queryset(self):

        queryset = (
            Notification.objects
            .filter(
                recipient=self.request.user
            )
        )

        unread = self.request.query_params.get(
            "unread"
        )

        if unread == "true":
            queryset = queryset.filter(
                is_read=False
            )

        elif unread == "false":
            queryset = queryset.filter(
                is_read=True
            )

        return queryset


class NotificationUnreadCountAPIView(
    APIView
):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        count = (
            Notification.objects
            .filter(
                recipient=request.user,
                is_read=False,
            )
            .count()
        )

        return Response(
            {
                "unread_count": count,
            }
        )


class NotificationMarkReadAPIView(
    APIView
):

    permission_classes = [
        IsAuthenticated
    ]

    def post(
        self,
        request,
        pk,
    ):

        notification = get_object_or_404(
            Notification,
            pk=pk,
            recipient=request.user,
        )

        mark_notification_read(
            notification=notification
        )

        serializer = NotificationSerializer(
            notification
        )

        return Response(
            serializer.data
        )


class NotificationMarkAllReadAPIView(
    APIView
):

    permission_classes = [
        IsAuthenticated
    ]

    def post(
        self,
        request,
    ):

        updated_count = (
            mark_all_notifications_read(
                user=request.user
            )
        )

        return Response(
            {
                "updated_count": (
                    updated_count
                )
            }
        )