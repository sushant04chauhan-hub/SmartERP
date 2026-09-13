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
            "expense_date": purchase_order.received_date,
            "reference_number": purchase_order.order_number,
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
            "revenue_date": sales_order.completed_date,
            "reference_number": sales_order.order_number,
            "created_by": user,
        },
    )

    return revenue, created