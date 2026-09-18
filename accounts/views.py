from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db import models
from django.db.models.functions import TruncMonth
from django.shortcuts import render

from hr.models import Department, Employee
from inventory.models import Product
from finance.models import Expense, Revenue
from procurement.models import PurchaseOrder, PurchaseOrderItem
from sales.models import SalesOrder, SalesOrderItem
from sales.forecasting import get_all_product_forecasts


class SmartERPLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


@login_required
def dashboard(request):

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

    demand_forecasts = get_all_product_forecasts()

    top_demand_forecasts = sorted(
        demand_forecasts,
        key=lambda item: item["predicted_demand"],
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
        demand_forecasts[0]["forecast_month"]
        if demand_forecasts
        else None
    )

    return render(
        request,
        "accounts/dashboard.html",
        {
            "employee_count": employee_count,
            "department_count": department_count,
            "active_employee_count": active_employee_count,
            "product_count": product_count,
            "low_stock_count": low_stock_count,
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
            "inventory_value": inventory_value,
            "inventory_status_labels": inventory_status_labels,
            "inventory_status_data": inventory_status_data,
            "expense_category_labels": expense_category_labels,
            "expense_category_data": expense_category_data,
            "demand_forecasts": demand_forecasts,
            "forecast_chart_labels": forecast_chart_labels,
            "forecast_chart_data": forecast_chart_data,
            "forecast_month": forecast_month,
        },
    )