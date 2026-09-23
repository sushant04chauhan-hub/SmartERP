from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from audit.services import record_audit_log
from finance.services import (
    create_revenue_for_sales_order,
)
from inventory.models import Product
from inventory.services import apply_stock_movement
from notifications.services import (
    create_notifications_for_roles,
)

from .models import SalesOrder


@transaction.atomic
def confirm_sales_order(
    *,
    sales_order,
    user,
):

    sales_order = (
        SalesOrder.objects
        .select_for_update()
        .get(pk=sales_order.pk)
    )

    if sales_order.status != "DRAFT":
        raise ValidationError(
            "Only draft sales orders can be confirmed."
        )

    if not sales_order.items.exists():
        raise ValidationError(
            "A sales order without items cannot be confirmed."
        )

    previous_status = sales_order.status

    sales_order.status = "CONFIRMED"

    sales_order.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    record_audit_log(
        user=user,
        action="CONFIRM",
        instance=sales_order,
        description=(
            f"Confirmed sales order "
            f"{sales_order.order_number}."
        ),
        metadata={
            "order_number": (
                sales_order.order_number
            ),
            "previous_status": previous_status,
            "new_status": sales_order.status,
        },
    )

    create_notifications_for_roles(
        roles={"SALES"},
        title="Sales order confirmed",
        message=(
            f"Sales order "
            f"{sales_order.order_number} "
            f"has been confirmed."
        ),
        notification_type="SUCCESS",
        priority="NORMAL",
        instance=sales_order,
        target_url="/sales",
        exclude_user=user,
    )

    return sales_order


@transaction.atomic
def cancel_sales_order(
    *,
    sales_order,
    user,
):

    sales_order = (
        SalesOrder.objects
        .select_for_update()
        .get(pk=sales_order.pk)
    )

    if sales_order.status not in {
        "DRAFT",
        "CONFIRMED",
    }:

        raise ValidationError(
            "Only draft or confirmed sales orders can be cancelled."
        )

    previous_status = sales_order.status

    sales_order.status = "CANCELLED"

    sales_order.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    record_audit_log(
        user=user,
        action="CANCEL",
        instance=sales_order,
        description=(
            f"Cancelled sales order "
            f"{sales_order.order_number}."
        ),
        metadata={
            "order_number": (
                sales_order.order_number
            ),
            "previous_status": previous_status,
            "new_status": sales_order.status,
        },
    )

    create_notifications_for_roles(
        roles={"SALES"},
        title="Sales order cancelled",
        message=(
            f"Sales order "
            f"{sales_order.order_number} "
            f"has been cancelled."
        ),
        notification_type="WARNING",
        priority="NORMAL",
        instance=sales_order,
        target_url="/sales",
        exclude_user=user,
    )

    return sales_order


@transaction.atomic
def complete_sales_order(
    *,
    sales_order,
    user,
):

    sales_order = (
        SalesOrder.objects
        .select_for_update()
        .get(pk=sales_order.pk)
    )

    if sales_order.status != "CONFIRMED":
        raise ValidationError(
            "Only confirmed sales orders can be completed."
        )

    items = list(
        sales_order.items.select_related(
            "product"
        )
    )

    if not items:
        raise ValidationError(
            "A sales order without items cannot be completed."
        )

    required_quantities = {}

    for item in items:

        required_quantities[
            item.product_id
        ] = (
            required_quantities.get(
                item.product_id,
                0,
            )
            + item.quantity
        )

    products = {
        product.id: product

        for product in (
            Product.objects
            .select_for_update()
            .filter(
                id__in=required_quantities.keys()
            )
        )
    }

    for (
        product_id,
        required_quantity,
    ) in required_quantities.items():

        product = products[
            product_id
        ]

        if (
            product.quantity
            < required_quantity
        ):

            raise ValidationError(
                (
                    f"Insufficient stock for "
                    f"{product.name}. "
                    f"Available: "
                    f"{product.quantity}, "
                    f"required: "
                    f"{required_quantity}."
                )
            )

    previous_status = sales_order.status

    for item in items:

        apply_stock_movement(
            product=item.product,
            movement_type="SALE",
            quantity=item.quantity,
            user=user,
            reference=sales_order.order_number,
            note=(
                "Stock issued for sales order"
            ),
        )

    sales_order.status = "COMPLETED"

    sales_order.completed_date = (
        timezone.localdate()
    )

    sales_order.save(
        update_fields=[
            "status",
            "completed_date",
            "updated_at",
        ]
    )

    create_revenue_for_sales_order(
        sales_order=sales_order,
        user=user,
    )

    record_audit_log(
        user=user,
        action="COMPLETE",
        instance=sales_order,
        description=(
            f"Completed sales order "
            f"{sales_order.order_number}."
        ),
        metadata={
            "order_number": (
                sales_order.order_number
            ),
            "previous_status": previous_status,
            "new_status": sales_order.status,
            "completed_date": str(
                sales_order.completed_date
            ),
        },
    )

    create_notifications_for_roles(
        roles={"SALES"},
        title="Sales order completed",
        message=(
            f"Sales order "
            f"{sales_order.order_number} "
            f"has been completed."
        ),
        notification_type="SUCCESS",
        priority="NORMAL",
        instance=sales_order,
        target_url="/sales",
        exclude_user=user,
    )

    return sales_order