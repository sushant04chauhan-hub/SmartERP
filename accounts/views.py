from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render

from .dashboard_data import build_dashboard_data


class SmartERPLoginView(LoginView):

    template_name = "accounts/login.html"
    redirect_authenticated_user = True


@login_required
def dashboard(request):

    return render(
        request,
        "accounts/dashboard.html",
        build_dashboard_data(),
    )