from datetime import date
import numpy as np
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from sklearn.linear_model import LinearRegression

from inventory.models import Product
from .models import SalesOrderItem

def next_month(value):

    if value.month == 12:
        return date(
            value.year + 1,
            1,
            1,
        )

    return date(
        value.year,
        value.month + 1,
        1,
    )

def previous_month(value):

    if value.month == 1:
        return date(
            value.year - 1,
            12,
            1,
        )

    return date(
        value.year,
        value.month - 1,
        1,
    )

def get_monthly_product_demand(product):

    today = timezone.localdate()

    current_month = date(
        today.year,
        today.month,
        1,
    )

    last_complete_month = previous_month(
        current_month
    )

    first_month = last_complete_month

    for _ in range(11):
        first_month = previous_month(
            first_month
        )

    monthly_demand = (
        SalesOrderItem.objects
        .filter(
            product=product,
            sales_order__status="COMPLETED",
            sales_order__completed_date__isnull=False,
            sales_order__completed_date__gte=first_month,
            sales_order__completed_date__lt=current_month,
        )
        .annotate(
            month=TruncMonth(
                "sales_order__completed_date"
            )
        )
        .values("month")
        .annotate(
            quantity=Sum("quantity")
        )
        .order_by("month")
    )

    demand_by_month = {
        item["month"]: item["quantity"]
        for item in monthly_demand
        if item["month"] is not None
    }

    result = []

    month = first_month

    while month <= last_complete_month:

        result.append(
            {
                "month": month,
                "quantity": demand_by_month.get(
                    month,
                    0,
                ),
            }
        )

        month = next_month(month)

    return result

def forecast_product_demand(product):

    history = get_monthly_product_demand(
        product
    )

    if not history:
        return {
            "product_code": product.product_code,
            "product_name": product.name,
            "forecast_month": None,
            "predicted_demand": 0,
            "method": "No historical data",
            "historical_months": 0,
        }

    quantities = [
        item["quantity"]
        for item in history
    ]

    non_zero_months = sum(
        1
        for quantity in quantities
        if quantity > 0
    )

    forecast_month = next_month(
        history[-1]["month"]
    )

    if sum(quantities) == 0:

        predicted_demand = 0
        method = "No-demand fallback"

    elif non_zero_months < 3:

        predicted_demand = round(
            sum(quantities)
            / len(quantities)
        )

        method = "Historical average fallback"

    else:

        x = np.arange(
            len(quantities)
        ).reshape(-1, 1)

        y = np.array(
            quantities,
            dtype=float,
        )

        model = LinearRegression()

        model.fit(
            x,
            y,
        )

        prediction = model.predict(
            [[len(quantities)]]
        )[0]

        predicted_demand = max(
            0,
            round(float(prediction)),
        )

        method = "Linear Regression"

    return {
        "product_code": product.product_code,
        "product_name": product.name,
        "forecast_month": forecast_month,
        "predicted_demand": predicted_demand,
        "method": method,
        "historical_months": len(history),
    }

def get_all_product_forecasts():

    products = Product.objects.order_by(
        "product_code"
    )

    return [
        forecast_product_demand(product)
        for product in products
    ]