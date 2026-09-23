from django.core.exceptions import ValidationError
from django.db import transaction

from audit.services import record_audit_log
from notifications.services import (
    create_notifications_for_roles,
)

from .models import Product, StockMovement


INCOMING_MOVEMENT_TYPES = {
    "PURCHASE",
    "RETURN_IN",
    "ADJUSTMENT_IN",
}

OUTGOING_MOVEMENT_TYPES = {
    "SALE",
    "RETURN_OUT",
    "ADJUSTMENT_OUT",
    "DAMAGED",
}


@transaction.atomic
def apply_stock_movement(
    *,
    product,
    movement_type,
    quantity,
    user=None,
    reference="",
    note="",
):

    if quantity <= 0:
        raise ValidationError(
            "Quantity must be greater than zero."
        )

    valid_types = (
        INCOMING_MOVEMENT_TYPES
        | OUTGOING_MOVEMENT_TYPES
    )

    if movement_type not in valid_types:
        raise ValidationError(
            f"Invalid stock movement type: "
            f"{movement_type}"
        )

    product = (
        Product.objects
        .select_for_update()
        .get(pk=product.pk)
    )

    stock_before = product.quantity

    if movement_type in INCOMING_MOVEMENT_TYPES:

        product.quantity += quantity

    elif movement_type in OUTGOING_MOVEMENT_TYPES:

        if product.quantity < quantity:
            raise ValidationError(
                "Insufficient stock for this movement."
            )

        product.quantity -= quantity

    product.save()

    created_by = None

    if (
        user is not None
        and getattr(
            user,
            "is_authenticated",
            False,
        )
    ):
        created_by = user

    movement = StockMovement.objects.create(
        product=product,
        movement_type=movement_type,
        quantity=quantity,
        reference=reference.strip(),
        created_by=created_by,
        note=note.strip(),
    )

    if movement_type in {
        "ADJUSTMENT_IN",
        "ADJUSTMENT_OUT",
    }:
        audit_action = "ADJUST"

    elif movement_type in INCOMING_MOVEMENT_TYPES:
        audit_action = "STOCK_IN"

    else:
        audit_action = "STOCK_OUT"

    record_audit_log(
        user=user,
        action=audit_action,
        instance=movement,
        description=(
            f"Applied {movement_type} "
            f"stock movement of {quantity} "
            f"unit(s) for "
            f"{product.product_code} - "
            f"{product.name}."
        ),
        metadata={
            "product_id": product.id,
            "product_code": product.product_code,
            "movement_type": movement_type,
            "quantity": quantity,
            "reference": reference.strip(),
            "stock_before": stock_before,
            "stock_after": product.quantity,
        },
    )

    crossed_reorder_threshold = (
        stock_before > product.reorder_level
        and product.quantity
        <= product.reorder_level
    )

    if crossed_reorder_threshold:

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
                f"{product.name} has fallen to "
                f"{product.quantity} unit(s). "
                f"Reorder level: "
                f"{product.reorder_level}."
            )

        create_notifications_for_roles(
            roles={
                "INVENTORY",
                "MANAGER",
            },
            title="Low stock alert",
            message=message,
            notification_type=(
                "ACTION_REQUIRED"
            ),
            priority=priority,
            module="inventory",
            entity_type="inventory.Product",
            entity_id=str(product.id),
            target_url="/inventory",
            exclude_user=user,
        )

    return product, movement