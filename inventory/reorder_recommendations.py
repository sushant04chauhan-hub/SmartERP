from inventory.models import Product
from sales.forecasting import forecast_product_demand


def get_reorder_recommendation(product):

    forecast = forecast_product_demand(
        product
    )

    predicted_demand = forecast[
        "predicted_demand"
    ]

    projected_stock = (
        product.quantity
        - predicted_demand
    )

    if projected_stock <= product.reorder_level:

        action = "REORDER"

        target_stock = (
            predicted_demand
            + product.reorder_level
            + product.safety_stock
        )

        recommended_quantity = max(
            0,
            target_stock - product.quantity,
        )

        if projected_stock <= 0:
            urgency = "CRITICAL"

        elif projected_stock <= product.safety_stock:
            urgency = "HIGH"

        else:
            urgency = "MEDIUM"

    else:

        action = "NO_ACTION"
        recommended_quantity = 0
        urgency = "NONE"

    return {
        "product_code": product.product_code,
        "product_name": product.name,
        "current_stock": product.quantity,
        "predicted_demand": predicted_demand,
        "projected_stock": projected_stock,
        "reorder_level": product.reorder_level,
        "safety_stock": product.safety_stock,
        "action": action,
        "urgency": urgency,
        "recommended_quantity": recommended_quantity,
        "forecast_month": forecast[
            "forecast_month"
        ],
        "forecast_method": forecast[
            "method"
        ],
    }


def get_all_reorder_recommendations():

    products = Product.objects.order_by(
        "product_code"
    )

    recommendations = [
        get_reorder_recommendation(product)
        for product in products
    ]

    urgency_order = {
        "CRITICAL": 0,
        "HIGH": 1,
        "MEDIUM": 2,
        "NONE": 3,
    }

    return sorted(
        recommendations,
        key=lambda item: (
            urgency_order[item["urgency"]],
            item["projected_stock"],
            item["product_code"],
        ),
    )