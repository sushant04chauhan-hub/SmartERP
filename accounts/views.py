from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render

from hr.models import Employee


class SmartERPLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


@login_required
def dashboard(request):
    employee_count = Employee.objects.count()

    return render(
        request,
        "accounts/dashboard.html",
        {
            "employee_count": employee_count,
        },
    )