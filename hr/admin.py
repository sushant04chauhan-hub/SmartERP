from django.contrib import admin

from .models import Department, Employee


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "employee_id",
        "first_name",
        "last_name",
        "department",
        "designation",
        "status",
    )

    list_filter = (
        "department",
        "status",
    )

    search_fields = (
        "employee_id",
        "first_name",
        "last_name",
        "email",
    )

    ordering = ("employee_id",)