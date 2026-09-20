from datetime import datetime

from django.db import models
from django.db.models.functions import TruncMonth

from finance.anomaly_detection import detect_expense_anomalies
from finance.models import Expense, Revenue
from hr.models import Department, Employee
from inventory.models import Product
from inventory.reorder_recommendations import (
    get_all_reorder_recommendations,
)
from procurement.models import PurchaseOrder
from procurement.supplier_scoring import get_supplier_scores
from sales.forecasting import get_all_product_forecasts
from sales.models import SalesOrder, SalesOrderItem


def build_dashboard_data():

    employee_count = Employee.objects.count()

    department_count = Department.objects.count()

    active_employee_count = Employee.objects.filter(
        status="ACTIVE"
    ).count()

    product_count = Product.objects.count()

    low_stock_count = Product.objects.filter(
        quantity__lte=models.F("reorder_level")
    ).count()

    total_revenue = (
        Revenue.objects.aggregate(
            total=models.Sum("amount")
        )["total"]
        or 0
    )

    total_paid_expenses = (
        Expense.objects.filter(
            status="PAID"
        ).aggregate(
            total=models.Sum("amount")
        )["total"]
        or 0
    )

    pending_expense_count = Expense.objects.filter(
        status="PENDING"
    ).count()

    completed_sales_count = SalesOrder.objects.filter(
        status="COMPLETED"
    ).count()

    received_purchase_count = PurchaseOrder.objects.filter(
        status="RECEIVED"
    ).count()

    monthly_revenue = (
        Revenue.objects
        .annotate(
            month=TruncMonth("revenue_date")
        )
        .values("month")
        .annotate(
            total=models.Sum("amount")
        )
        .order_by("month")
    )

    revenue_chart_labels = [
        item["month"].strftime("%b %Y")
        for item in monthly_revenue
    ]

    revenue_chart_data = [
        float(item["total"])
        for item in monthly_revenue
    ]

    monthly_paid_expenses = (
        Expense.objects.filter(
            status="PAID",
            paid_at__isnull=False,
        )
        .annotate(
            month=TruncMonth("paid_at")
        )
        .values("month")
        .annotate(
            total=models.Sum("amount")
        )
        .order_by("month")
    )

    revenue_by_month = {
        item["month"].strftime("%Y-%m"): float(item["total"])
        for item in monthly_revenue
    }

    expenses_by_month = {
        item["month"].strftime("%Y-%m"): float(item["total"])
        for item in monthly_paid_expenses
    }

    finance_months = sorted(
        set(revenue_by_month)
        | set(expenses_by_month)
    )

    finance_chart_labels = [
        datetime.strptime(
            month,
            "%Y-%m",
        ).strftime("%b %Y")
        for month in finance_months
    ]

    finance_revenue_data = [
        revenue_by_month.get(
            month,
            0,
        )
        for month in finance_months
    ]

    finance_expense_data = [
        expenses_by_month.get(
            month,
            0,
        )
        for month in finance_months
    ]

    top_selling_products = (
        SalesOrderItem.objects.filter(
            sales_order__status="COMPLETED"
        )
        .values(
            "product__product_code",
            "product__name",
        )
        .annotate(
            total_quantity=models.Sum("quantity")
        )
        .order_by(
            "-total_quantity",
            "product__name",
        )[:5]
    )

    top_product_labels = [
        item["product__name"]
        for item in top_selling_products
    ]

    top_product_data = [
        item["total_quantity"]
        for item in top_selling_products
    ]

    monthly_procurement = (
        PurchaseOrder.objects.filter(
            status="RECEIVED",
            received_date__isnull=False,
        )
        .annotate(
            month=TruncMonth("received_date")
        )
        .values("month")
        .annotate(
            total=models.Sum("total_amount")
        )
        .order_by("month")
    )

    procurement_chart_labels = [
        item["month"].strftime("%b %Y")
        for item in monthly_procurement
    ]

    procurement_chart_data = [
        float(item["total"])
        for item in monthly_procurement
    ]

    top_suppliers = (
        PurchaseOrder.objects.filter(
            status="RECEIVED"
        )
        .values(
            "supplier__name"
        )
        .annotate(
            total_value=models.Sum("total_amount")
        )
        .order_by(
            "-total_value",
            "supplier__name",
        )[:5]
    )

    top_supplier_labels = [
        item["supplier__name"]
        for item in top_suppliers
    ]

    top_supplier_data = [
        float(item["total_value"])
        for item in top_suppliers
    ]

    inventory_value = (
        Product.objects.aggregate(
            total=models.Sum(
                models.F("quantity")
                * models.F("purchase_price"),
                output_field=models.DecimalField(
                    max_digits=18,
                    decimal_places=2,
                ),
            )
        )["total"]
        or 0
    )

    out_of_stock_count = Product.objects.filter(
        quantity=0
    ).count()

    low_stock_inventory_count = Product.objects.filter(
        quantity__gt=0,
        quantity__lte=models.F("reorder_level"),
    ).count()

    healthy_stock_count = Product.objects.filter(
        quantity__gt=models.F("reorder_level")
    ).count()

    inventory_status_labels = [
        "Healthy Stock",
        "Low Stock",
        "Out of Stock",
    ]

    inventory_status_data = [
        healthy_stock_count,
        low_stock_inventory_count,
        out_of_stock_count,
    ]

    expense_by_category = (
        Expense.objects.filter(
            status="PAID"
        )
        .values(
            "category"
        )
        .annotate(
            total=models.Sum("amount")
        )
        .order_by(
            "-total"
        )
    )

    expense_category_labels = [
        dict(Expense.CATEGORY_CHOICES).get(
            item["category"],
            item["category"],
        )
        for item in expense_by_category
    ]

    expense_category_data = [
        float(item["total"])
        for item in expense_by_category
    ]

    demand_forecasts = (
        get_all_product_forecasts()
    )

    top_demand_forecasts = sorted(
        demand_forecasts,
        key=lambda item: item[
            "predicted_demand"
        ],
        reverse=True,
    )[:5]

    forecast_chart_labels = [
        item["product_name"]
        for item in top_demand_forecasts
    ]

    forecast_chart_data = [
        item["predicted_demand"]
        for item in top_demand_forecasts
    ]

    forecast_month = (
        demand_forecasts[0][
            "forecast_month"
        ]
        if demand_forecasts
        else None
    )

    expense_anomaly_results = (
        detect_expense_anomalies()
    )

    expense_anomalies = [
        item
        for item in expense_anomaly_results
        if item["is_anomaly"]
    ]

    expense_anomaly_count = len(
        expense_anomalies
    )

    top_expense_anomalies = (
        expense_anomalies[:5]
    )

    supplier_scores = (
        get_supplier_scores()
    )

    top_supplier_scores = (
        supplier_scores[:5]
    )

    supplier_score_labels = [
        item["supplier_name"]
        for item in top_supplier_scores
    ]

    supplier_score_data = [
        item["supplier_score"]
        for item in top_supplier_scores
    ]

    reorder_recommendations = (
        get_all_reorder_recommendations()
    )

    reorder_items = [
        item
        for item in reorder_recommendations
        if item["action"] == "REORDER"
    ]

    reorder_recommendation_count = len(
        reorder_items
    )

    top_reorder_recommendations = (
        reorder_items[:5]
    )

    return {
        "employee_count": employee_count,
        "department_count": department_count,
        "active_employee_count": active_employee_count,

        "product_count": product_count,
        "low_stock_count": low_stock_count,
        "inventory_value": inventory_value,

        "total_revenue": total_revenue,
        "total_paid_expenses": total_paid_expenses,
        "pending_expense_count": pending_expense_count,

        "completed_sales_count": completed_sales_count,
        "received_purchase_count": received_purchase_count,

        "revenue_chart_labels": revenue_chart_labels,
        "revenue_chart_data": revenue_chart_data,

        "finance_chart_labels": finance_chart_labels,
        "finance_revenue_data": finance_revenue_data,
        "finance_expense_data": finance_expense_data,

        "top_product_labels": top_product_labels,
        "top_product_data": top_product_data,

        "procurement_chart_labels": procurement_chart_labels,
        "procurement_chart_data": procurement_chart_data,

        "top_supplier_labels": top_supplier_labels,
        "top_supplier_data": top_supplier_data,

        "inventory_status_labels": inventory_status_labels,
        "inventory_status_data": inventory_status_data,

        "expense_category_labels": expense_category_labels,
        "expense_category_data": expense_category_data,

        "demand_forecasts": demand_forecasts,
        "forecast_chart_labels": forecast_chart_labels,
        "forecast_chart_data": forecast_chart_data,
        "forecast_month": forecast_month,

        "expense_anomaly_count": expense_anomaly_count,
        "top_expense_anomalies": top_expense_anomalies,

        "supplier_scores": supplier_scores,
        "supplier_score_labels": supplier_score_labels,
        "supplier_score_data": supplier_score_data,

        "reorder_recommendations": reorder_recommendations,
        "reorder_items": reorder_items,
        "reorder_recommendation_count": reorder_recommendation_count,
        "top_reorder_recommendations": top_reorder_recommendations,
    }