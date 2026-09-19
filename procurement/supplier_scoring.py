from decimal import Decimal

from .models import Supplier


def get_supplier_performance():

    suppliers = (
        Supplier.objects
        .prefetch_related("purchase_orders")
        .order_by("name")
    )

    results = []

    for supplier in suppliers:

        purchase_orders = list(
            supplier.purchase_orders.all()
        )

        total_orders = len(
            purchase_orders
        )

        received_orders = [
            purchase_order
            for purchase_order in purchase_orders
            if purchase_order.status == "RECEIVED"
        ]

        cancelled_orders = [
            purchase_order
            for purchase_order in purchase_orders
            if purchase_order.status == "CANCELLED"
        ]

        total_received_value = sum(
            (
                purchase_order.total_amount
                for purchase_order
                in received_orders
            ),
            Decimal("0.00"),
        )

        delivery_orders = [
            purchase_order
            for purchase_order in received_orders
            if (
                purchase_order.expected_delivery_date
                and purchase_order.received_date
            )
        ]

        on_time_deliveries = 0
        total_delay_days = 0

        for purchase_order in delivery_orders:

            delay_days = (
                purchase_order.received_date
                - purchase_order.expected_delivery_date
            ).days

            if delay_days <= 0:
                on_time_deliveries += 1
            else:
                total_delay_days += delay_days

        delivery_count = len(
            delivery_orders
        )

        if delivery_count:
            on_time_rate = (
                on_time_deliveries
                / delivery_count
            ) * 100

            average_delay_days = (
                total_delay_days
                / delivery_count
            )
        else:
            on_time_rate = 0
            average_delay_days = 0

        if total_orders:
            cancellation_rate = (
                len(cancelled_orders)
                / total_orders
            ) * 100
        else:
            cancellation_rate = 0

        results.append(
            {
                "supplier_id": supplier.id,
                "supplier_name": supplier.name,
                "total_orders": total_orders,
                "received_orders": len(
                    received_orders
                ),
                "cancelled_orders": len(
                    cancelled_orders
                ),
                "total_received_value": float(
                    total_received_value
                ),
                "delivery_records": delivery_count,
                "on_time_deliveries": (
                    on_time_deliveries
                ),
                "on_time_rate": round(
                    on_time_rate,
                    2,
                ),
                "average_delay_days": round(
                    average_delay_days,
                    2,
                ),
                "cancellation_rate": round(
                    cancellation_rate,
                    2,
                ),
            }
        )

    return results

def calculate_supplier_score(performance):

    total_orders = performance["total_orders"]
    received_orders = performance["received_orders"]
    delivery_records = performance["delivery_records"]

    if total_orders == 0:
        fulfillment_rate = 0
    else:
        fulfillment_rate = (
            received_orders
            / total_orders
        ) * 100

    on_time_score = performance[
        "on_time_rate"
    ]

    delay_score = max(
        0,
        100
        - (
            performance["average_delay_days"]
            * 20
        ),
    )

    cancellation_score = max(
        0,
        100
        - performance["cancellation_rate"],
    )

    if received_orders:
        delivery_data_coverage = (
            delivery_records
            / received_orders
        )
    else:
        delivery_data_coverage = 0

    confidence_score = (
        min(
            delivery_records / 5,
            1,
        )
        * delivery_data_coverage
        * 100
    )

    score = (
        (on_time_score * 0.30)
        + (delay_score * 0.15)
        + (cancellation_score * 0.20)   
        + (fulfillment_rate * 0.25)
        + (confidence_score * 0.10)
    )

    return round(
        score,
        2,
    )

def get_supplier_rating(score):

    if score >= 85:
        return "EXCELLENT"

    if score >= 70:
        return "GOOD"

    if score >= 55:
        return "FAIR"

    return "NEEDS_REVIEW"

def get_supplier_scores():

    performance_results = (
        get_supplier_performance()
    )

    results = []

    for performance in performance_results:

        score = calculate_supplier_score(
            performance
        )

        results.append(
            {
                **performance,
                "supplier_score": score,
                "rating": get_supplier_rating(
                    score
                ),
            }
        )

    return sorted(
        results,
        key=lambda item: (
            -item["supplier_score"],
            item["supplier_name"],
        ),
    )