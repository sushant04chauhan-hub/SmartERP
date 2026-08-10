from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render

from hr.models import Department, Employee


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

    return render(
        request,
        "accounts/dashboard.html",
        {
            "employee_count": employee_count,
            "department_count": department_count,
            "active_employee_count": active_employee_count,
        },
    )