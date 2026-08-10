from django.urls import path

from .views import (
    employee_create,
    employee_delete,
    employee_list,
    employee_update,
)


urlpatterns = [
    path("employees/", employee_list, name="employee_list"),
    path(
        "employees/add/",
        employee_create,
        name="employee_create",
    ),

    path(
        "employees/<int:employee_id>/edit/",
        employee_update,
        name="employee_update",
    ),

    path(
        "employees/<int:employee_id>/delete/",
        employee_delete,
        name="employee_delete",
    ),
]