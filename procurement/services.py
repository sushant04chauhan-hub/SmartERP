from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from inventory.services import apply_stock_movement
from finance.services import create_expense_for_purchase_order

from .models import PurchaseOrder


@transaction.atomic
def approve_purchase_order(*, purchase_order, user):

    purchase_order = (
        PurchaseOrder.objects
        .select_for_update()
        .get(pk=purchase_order.pk)
    )

    if purchase_order.status != "DRAFT":
        raise ValidationError(
            "Only draft purchase orders can be approved."
        )

    purchase_order.status = "APPROVED"
    purchase_order.approved_by = user

    purchase_order.save(
        update_fields=[
            "status",
            "approved_by",
            "updated_at",
        ]
    )

    return purchase_order


@transaction.atomic
def mark_purchase_order_ordered(*, purchase_order):

    purchase_order = (
        PurchaseOrder.objects
        .select_for_update()
        .get(pk=purchase_order.pk)
    )

    if purchase_order.status != "APPROVED":
        raise ValidationError(
            "Only approved purchase orders can be marked as ordered."
        )

    purchase_order.status = "ORDERED"

    purchase_order.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    return purchase_order


@transaction.atomic
def receive_purchase_order(*, purchase_order, user):

    purchase_order = (
        PurchaseOrder.objects
        .select_for_update()
        .get(pk=purchase_order.pk)
    )

    # PENDING is temporarily supported for old purchase orders.
    if purchase_order.status != "ORDERED":
        raise ValidationError(
            "Only ordered purchase orders can be received."
        )

    items = purchase_order.items.select_related(
        "product"
    ).all()

    if not items.exists():
        raise ValidationError(
            "A purchase order without items cannot be received."
        )

    for item in items:

        apply_stock_movement(
            product=item.product,
            movement_type="PURCHASE",
            quantity=item.quantity,
            user=user,
            reference=purchase_order.order_number,
            note="Stock received from purchase order",
        )

    purchase_order.status = "RECEIVED"
    purchase_order.received_date = timezone.localdate()

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

    return purchase_order


@transaction.atomic
def cancel_purchase_order(*, purchase_order):

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

    purchase_order.status = "CANCELLED"

    purchase_order.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    return purchase_order