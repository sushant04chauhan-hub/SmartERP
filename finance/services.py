from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from audit.services import record_audit_log
from notifications.services import (
    create_notification,
    create_notifications_for_roles,
)

from .models import Expense, Revenue


def create_expense_for_purchase_order(
    *,
    purchase_order,
    user,
):

    expense, created = Expense.objects.get_or_create(
        purchase_order=purchase_order,
        defaults={
            "title": (
                f"Purchase Order "
                f"{purchase_order.order_number}"
            ),
            "category": "PROCUREMENT",
            "amount": purchase_order.total_amount,
            "expense_date": (
                purchase_order.received_date
            ),
            "reference_number": (
                purchase_order.order_number
            ),
            "description": (
                "Automatically created from "
                f"purchase order "
                f"{purchase_order.order_number} "
                f"for supplier "
                f"{purchase_order.supplier.name}."
            ),
            "status": "PENDING",
            "created_by": user,
        },
    )

    if created:

        record_audit_log(
            user=user,
            action="CREATE",
            instance=expense,
            description=(
                f"Created procurement expense "
                f"for purchase order "
                f"{purchase_order.order_number}."
            ),
            metadata={
                "purchase_order": (
                    purchase_order.order_number
                ),
                "amount": str(expense.amount),
                "status": expense.status,
            },
        )

        create_notifications_for_roles(
            roles={
                "FINANCE",
                "MANAGER",
            },
            title="Expense requires review",
            message=(
                f"Procurement expense for "
                f"{purchase_order.order_number} "
                f"requires finance review."
            ),
            notification_type=(
                "ACTION_REQUIRED"
            ),
            priority="HIGH",
            instance=expense,
            target_url="/finance",
            exclude_user=user,
        )

    return expense, created


def create_revenue_for_sales_order(
    *,
    sales_order,
    user,
):

    revenue, created = Revenue.objects.get_or_create(
        sales_order=sales_order,
        defaults={
            "amount": sales_order.total_amount,
            "revenue_date": (
                sales_order.completed_date
            ),
            "reference_number": (
                sales_order.order_number
            ),
            "created_by": user,
        },
    )

    if created:

        record_audit_log(
            user=user,
            action="CREATE",
            instance=revenue,
            description=(
                f"Created revenue for "
                f"sales order "
                f"{sales_order.order_number}."
            ),
            metadata={
                "sales_order": (
                    sales_order.order_number
                ),
                "amount": str(revenue.amount),
            },
        )

        create_notifications_for_roles(
            roles={"FINANCE"},
            title="Sales revenue recorded",
            message=(
                f"Revenue for sales order "
                f"{sales_order.order_number} "
                f"has been recorded."
            ),
            notification_type="INFO",
            priority="NORMAL",
            instance=revenue,
            target_url="/finance",
            exclude_user=user,
        )

    return revenue, created


@transaction.atomic
def approve_expense(
    *,
    expense,
    user,
):

    expense = (
        Expense.objects
        .select_for_update()
        .get(pk=expense.pk)
    )

    if expense.status != "PENDING":
        raise ValidationError(
            "Only pending expenses can be approved."
        )

    previous_status = expense.status

    expense.status = "APPROVED"
    expense.reviewed_by = user
    expense.reviewed_at = timezone.now()

    expense.save(
        update_fields=[
            "status",
            "reviewed_by",
            "reviewed_at",
            "updated_at",
        ]
    )

    record_audit_log(
        user=user,
        action="APPROVE",
        instance=expense,
        description=(
            f"Approved expense "
            f"{expense.title}."
        ),
        metadata={
            "reference_number": (
                expense.reference_number
            ),
            "previous_status": previous_status,
            "new_status": expense.status,
            "amount": str(expense.amount),
        },
    )

    if (
        expense.created_by
        and expense.created_by_id
        != user.id
    ):

        create_notification(
            recipient=expense.created_by,
            title="Expense approved",
            message=(
                f"Expense "
                f"{expense.title} "
                f"has been approved."
            ),
            notification_type="SUCCESS",
            priority="NORMAL",
            instance=expense,
            target_url="/finance",
        )

    return expense


@transaction.atomic
def reject_expense(
    *,
    expense,
    user,
):

    expense = (
        Expense.objects
        .select_for_update()
        .get(pk=expense.pk)
    )

    if expense.status != "PENDING":
        raise ValidationError(
            "Only pending expenses can be rejected."
        )

    previous_status = expense.status

    expense.status = "REJECTED"
    expense.reviewed_by = user
    expense.reviewed_at = timezone.now()

    expense.save(
        update_fields=[
            "status",
            "reviewed_by",
            "reviewed_at",
            "updated_at",
        ]
    )

    record_audit_log(
        user=user,
        action="REJECT",
        instance=expense,
        description=(
            f"Rejected expense "
            f"{expense.title}."
        ),
        metadata={
            "reference_number": (
                expense.reference_number
            ),
            "previous_status": previous_status,
            "new_status": expense.status,
            "amount": str(expense.amount),
        },
    )

    if (
        expense.created_by
        and expense.created_by_id
        != user.id
    ):

        create_notification(
            recipient=expense.created_by,
            title="Expense rejected",
            message=(
                f"Expense "
                f"{expense.title} "
                f"has been rejected."
            ),
            notification_type="WARNING",
            priority="HIGH",
            instance=expense,
            target_url="/finance",
        )

    return expense


@transaction.atomic
def mark_expense_paid(
    *,
    expense,
    user,
    payment_method,
):

    expense = (
        Expense.objects
        .select_for_update()
        .get(pk=expense.pk)
    )

    if expense.status != "APPROVED":
        raise ValidationError(
            "Only approved expenses can be "
            "marked as paid."
        )

    valid_payment_methods = {
        choice[0]
        for choice
        in Expense.PAYMENT_METHOD_CHOICES
    }

    if (
        payment_method
        not in valid_payment_methods
    ):
        raise ValidationError(
            "A valid payment method is required."
        )

    previous_status = expense.status

    expense.status = "PAID"
    expense.payment_method = payment_method
    expense.paid_at = timezone.now()

    expense.save(
        update_fields=[
            "status",
            "payment_method",
            "paid_at",
            "updated_at",
        ]
    )

    record_audit_log(
        user=user,
        action="PAY",
        instance=expense,
        description=(
            f"Marked expense "
            f"{expense.title} as paid."
        ),
        metadata={
            "reference_number": (
                expense.reference_number
            ),
            "previous_status": previous_status,
            "new_status": expense.status,
            "payment_method": (
                payment_method
            ),
            "amount": str(expense.amount),
        },
    )

    if (
        expense.created_by
        and expense.created_by_id
        != user.id
    ):

        create_notification(
            recipient=expense.created_by,
            title="Expense paid",
            message=(
                f"Expense "
                f"{expense.title} "
                f"has been marked as paid."
            ),
            notification_type="SUCCESS",
            priority="NORMAL",
            instance=expense,
            target_url="/finance",
        )

    return expense