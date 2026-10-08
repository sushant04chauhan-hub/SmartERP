from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import F
from django.db.utils import OperationalError
from django.utils import timezone

from notifications.models import Notification
from notifications.services import create_notification

from .models import Product


User = get_user_model()


TASK_RETRY_OPTIONS = {
    "autoretry_for": (
        OperationalError,
    ),
    "retry_backoff": True,
    "retry_backoff_max": 60,
    "retry_jitter": True,
    "retry_kwargs": {
        "max_retries": 3,
    },
}


@shared_task(
    **TASK_RETRY_OPTIONS,
)
def build_inventory_health_snapshot():
    total_products = (
        Product.objects.count()
    )

    low_stock_products = (
        Product.objects.filter(
            quantity__lte=F(
                "reorder_level"
            )
        ).count()
    )

    below_safety_stock_products = (
        Product.objects.filter(
            quantity__lte=F(
                "safety_stock"
            )
        ).count()
    )

    out_of_stock_products = (
        Product.objects.filter(
            quantity=0
        ).count()
    )

    return {
        "total_products": (
            total_products
        ),
        "low_stock_products": (
            low_stock_products
        ),
        "below_safety_stock_products": (
            below_safety_stock_products
        ),
        "out_of_stock_products": (
            out_of_stock_products
        ),
    }


@shared_task(
    **TASK_RETRY_OPTIONS,
)
def monitor_low_stock_products():
    low_stock_products = (
        Product.objects
        .filter(
            quantity__lte=F(
                "reorder_level"
            )
        )
        .order_by("id")
    )

    recipients = (
        User.objects
        .filter(
            is_active=True,
            profile__role__in={
                "INVENTORY",
                "MANAGER",
            },
        )
        .distinct()
    )

    cooldown_hours = getattr(
        settings,
        "LOW_STOCK_NOTIFICATION_COOLDOWN_HOURS",
        24,
    )

    cooldown_start = (
        timezone.now()
        - timedelta(
            hours=cooldown_hours
        )
    )

    notifications_created = 0
    notifications_skipped = 0

    for product in low_stock_products:

        if product.quantity == 0:
            priority = "CRITICAL"

            message = (
                f"{product.product_code} - "
                f"{product.name} is out of stock."
            )
        else:
            priority = "HIGH"

            message = (
                f"{product.product_code} - "
                f"{product.name} has "
                f"{product.quantity} unit(s) "
                f"remaining. Reorder level: "
                f"{product.reorder_level}."
            )

        for recipient in recipients:

            recently_notified = (
                Notification.objects.filter(
                    recipient=recipient,
                    module="inventory",
                    entity_type=(
                        "inventory.Product"
                    ),
                    entity_id=str(
                        product.id
                    ),
                    title="Low stock alert",
                    created_at__gte=(
                        cooldown_start
                    ),
                ).exists()
            )

            if recently_notified:
                notifications_skipped += 1
                continue

            create_notification(
                recipient=recipient,
                title="Low stock alert",
                message=message,
                notification_type=(
                    "ACTION_REQUIRED"
                ),
                priority=priority,
                module="inventory",
                instance=product,
                target_url="/inventory",
            )

            notifications_created += 1

    return {
        "low_stock_products": (
            low_stock_products.count()
        ),
        "recipients": (
            recipients.count()
        ),
        "notifications_created": (
            notifications_created
        ),
        "notifications_skipped": (
            notifications_skipped
        ),
    }