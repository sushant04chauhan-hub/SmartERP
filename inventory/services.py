from django.core.exceptions import ValidationError
from django.db import transaction

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
    """
    Apply a stock movement safely.

    This function:
    1. Validates the movement.
    2. Locks the product row during the update.
    3. Updates current stock.
    4. Creates a StockMovement record.
    """

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
            f"Invalid stock movement type: {movement_type}"
        )

    # Lock this product row until the transaction finishes.
    product = Product.objects.select_for_update().get(
        pk=product.pk
    )

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

    if user is not None and getattr(
        user,
        "is_authenticated",
        False,
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

    return product, movement