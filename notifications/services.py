from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Notification


User = get_user_model()


def create_notification(
    *,
    recipient,
    title,
    message,
    notification_type="INFO",
    priority="NORMAL",
    module="",
    instance=None,
    entity_type="",
    entity_id="",
    target_url="",
):

    if instance is not None:

        module = (
            module
            or instance._meta.app_label
        )

        entity_type = (
            entity_type
            or instance._meta.label
        )

        entity_id = (
            entity_id
            or str(instance.pk or "")
        )

    return Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        priority=priority,
        title=title,
        message=message,
        module=module,
        entity_type=entity_type,
        entity_id=str(entity_id or ""),
        target_url=target_url,
    )


def create_notifications_for_roles(
    *,
    roles,
    title,
    message,
    notification_type="INFO",
    priority="NORMAL",
    module="",
    instance=None,
    entity_type="",
    entity_id="",
    target_url="",
    exclude_user=None,
):

    users = (
        User.objects
        .filter(
            is_active=True,
            profile__role__in=roles,
        )
        .distinct()
    )

    if (
        exclude_user is not None
        and getattr(
            exclude_user,
            "pk",
            None,
        )
    ):
        users = users.exclude(
            pk=exclude_user.pk
        )

    notifications = []

    for user in users:

        notifications.append(
            create_notification(
                recipient=user,
                title=title,
                message=message,
                notification_type=(
                    notification_type
                ),
                priority=priority,
                module=module,
                instance=instance,
                entity_type=entity_type,
                entity_id=entity_id,
                target_url=target_url,
            )
        )

    return notifications


def mark_notification_read(
    *,
    notification,
):

    if notification.is_read:
        return notification

    notification.is_read = True
    notification.read_at = timezone.now()

    notification.save(
        update_fields=[
            "is_read",
            "read_at",
        ]
    )

    return notification


def mark_all_notifications_read(
    *,
    user,
):

    return (
        Notification.objects
        .filter(
            recipient=user,
            is_read=False,
        )
        .update(
            is_read=True,
            read_at=timezone.now(),
        )
    )