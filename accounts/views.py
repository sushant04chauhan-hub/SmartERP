from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db import models
from django.shortcuts import render

from hr.models import Department, Employee
from inventory.models import Product


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

    return render(
        request,
        "accounts/dashboard.html",
        {
            "employee_count": employee_count,
            "department_count": department_count,
            "active_employee_count": active_employee_count,
            "product_count": product_count,
            "low_stock_count": low_stock_count,
        },
    )