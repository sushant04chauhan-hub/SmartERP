from django.urls import path

from .views import SmartERPLoginView, dashboard


urlpatterns = [
    path("login/", SmartERPLoginView.as_view(), name="login"),
    path("dashboard/", dashboard, name="dashboard"),
]