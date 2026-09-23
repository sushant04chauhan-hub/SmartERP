from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from audit.services import record_audit_log
from finance.services import (
    create_expense_for_purchase_order,
)
from inventory.services import apply_stock_movement
from notifications.services import (
    create_notifications_for_roles,
)

from .models import PurchaseOrder


@transaction.atomic
def approve_purchase_order(
    *,
    purchase_order,
    user,
):

    purchase_order = (
        PurchaseOrder.objects
        .select_for_update()
        .get(pk=purchase_order.pk)
    )

    if purchase_order.status != "DRAFT":
        raise ValidationError(
            "Only draft purchase orders can be approved."
        )

    previous_status = purchase_order.status

    purchase_order.status = "APPROVED"
    purchase_order.approved_by = user

    purchase_order.save(
        update_fields=[
            "status",
            "approved_by",
            "updated_at",
        ]
    )

    record_audit_log(
        user=user,
        action="APPROVE",
        instance=purchase_order,
        description=(
            f"Approved purchase order "
            f"{purchase_order.order_number}."
        ),
        metadata={
            "order_number": (
                purchase_order.order_number
            ),
            "previous_status": previous_status,
            "new_status": purchase_order.status,
        },
    )

    create_notifications_for_roles(
        roles={"PROCUREMENT"},
        title="Purchase order approved",
        message=(
            f"Purchase order "
            f"{purchase_order.order_number} "
            f"has been approved."
        ),
        notification_type="SUCCESS",
        priority="NORMAL",
        instance=purchase_order,
        target_url="/procurement",
        exclude_user=user,
    )

    return purchase_order


@transaction.atomic
def mark_purchase_order_ordered(
    *,
    purchase_order,
    user,
):

    purchase_order = (
        PurchaseOrder.objects
        .select_for_update()
        .get(pk=purchase_order.pk)
    )

    if purchase_order.status != "APPROVED":
        raise ValidationError(
            "Only approved purchase orders can be marked as ordered."
        )

    previous_status = purchase_order.status

    purchase_order.status = "ORDERED"

    purchase_order.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    record_audit_log(
        user=user,
        action="ORDER",
        instance=purchase_order,
        description=(
            f"Marked purchase order "
            f"{purchase_order.order_number} "
            f"as ordered."
        ),
        metadata={
            "order_number": (
                purchase_order.order_number
            ),
            "previous_status": previous_status,
            "new_status": purchase_order.status,
        },
    )

    create_notifications_for_roles(
        roles={"PROCUREMENT"},
        title="Purchase order placed",
        message=(
            f"Purchase order "
            f"{purchase_order.order_number} "
            f"has been marked as ordered."
        ),
        notification_type="INFO",
        priority="NORMAL",
        instance=purchase_order,
        target_url="/procurement",
        exclude_user=user,
    )

    return purchase_order


@transaction.atomic
def receive_purchase_order(
    *,
    purchase_order,
    user,
):

    purchase_order = (
        PurchaseOrder.objects
        .select_for_update()
        .get(pk=purchase_order.pk)
    )

    if purchase_order.status != "ORDERED":
        raise ValidationError(
            "Only ordered purchase orders can be received."
        )

    items = (
        purchase_order.items
        .select_related("product")
        .all()
    )

    if not items.exists():
        raise ValidationError(
            "A purchase order without items cannot be received."
        )

    previous_status = purchase_order.status

    for item in items:

        apply_stock_movement(
            product=item.product,
            movement_type="PURCHASE",
            quantity=item.quantity,
            user=user,
            reference=purchase_order.order_number,
            note=(
                "Stock received from "
                "purchase order"
            ),
        )

    purchase_order.status = "RECEIVED"
    purchase_order.received_date = (
        timezone.localdate()
    )

    purchase_order.save(
        update_fields=[
            "status",
            "received_date",
            "updated_at",
        ]
    )

    create_expense_for_purchase_order(
        purchase_order=purchase_order,
        user=user,
    )

    record_audit_log(
        user=user,
        action="RECEIVE",
        instance=purchase_order,
        description=(
            f"Received purchase order "
            f"{purchase_order.order_number}."
        ),
        metadata={
            "order_number": (
                purchase_order.order_number
            ),
            "previous_status": previous_status,
            "new_status": purchase_order.status,
            "received_date": str(
                purchase_order.received_date
            ),
        },
    )

    create_notifications_for_roles(
        roles={"PROCUREMENT"},
        title="Purchase order received",
        message=(
            f"Purchase order "
            f"{purchase_order.order_number} "
            f"has been received."
        ),
        notification_type="SUCCESS",
        priority="NORMAL",
        instance=purchase_order,
        target_url="/procurement",
        exclude_user=user,
    )

    return purchase_order


@transaction.atomic
def cancel_purchase_order(
    *,
    purchase_order,
    user,
):

    purchase_order = (
        PurchaseOrder.objects
        .select_for_update()
        .get(pk=purchase_order.pk)
    )

    if purchase_order.status not in {
        "DRAFT",
        "APPROVED",
        "ORDERED",
    }:

        raise ValidationError(
            "This purchase order cannot be cancelled."
        )

    previous_status = purchase_order.status

    purchase_order.status = "CANCELLED"

    purchase_order.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    record_audit_log(
        user=user,
        action="CANCEL",
        instance=purchase_order,
        description=(
            f"Cancelled purchase order "
            f"{purchase_order.order_number}."
        ),
        metadata={
            "order_number": (
                purchase_order.order_number
            ),
            "previous_status": previous_status,
            "new_status": purchase_order.status,
        },
    )

    create_notifications_for_roles(
        roles={"PROCUREMENT"},
        title="Purchase order cancelled",
        message=(
            f"Purchase order "
            f"{purchase_order.order_number} "
            f"has been cancelled."
        ),
        notification_type="WARNING",
        priority="NORMAL",
        instance=purchase_order,
        target_url="/procurement",
        exclude_user=user,
    )

    return purchase_order