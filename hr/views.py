from django.shortcuts import redirect, render
from accounts.decorators import role_required

from .forms import EmployeeForm
from .models import Department, Employee



@role_required("ADMIN", "MANAGER", "HR")
def employee_list(request):
    employees = Employee.objects.select_related("department").all()

    search = request.GET.get("search", "").strip()
    department = request.GET.get("department", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        employees = employees.filter(
            employee_id__icontains=search
        ) | employees.filter(
            first_name__icontains=search
        ) | employees.filter(
            last_name__icontains=search
        ) | employees.filter(
            email__icontains=search
        )

    if department:
        employees = employees.filter(
            department_id=department
        )

    if status:
        employees = employees.filter(
            status=status
        )

    employees = employees.distinct()

    departments = Department.objects.all().order_by("name")

    return render(
        request,
        "hr/employee_list.html",
        {
            "employees": employees,
            "departments": departments,
            "search": search,
            "selected_department": department,
            "selected_status": status,
            "employee_count": employees.count(),
        },
    )



@role_required("ADMIN", "MANAGER", "HR")
def employee_create(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("employee_list")

    else:
        form = EmployeeForm()

    return render(
        request,
        "hr/employee_form.html",
        {"form": form},
    )



@role_required("ADMIN", "MANAGER", "HR")
def employee_update(request, employee_id):
    employee = Employee.objects.get(id=employee_id)

    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=employee)

        if form.is_valid():
            form.save()
            return redirect("employee_list")

    else:
        form = EmployeeForm(instance=employee)

    return render(
        request,
        "hr/employee_form.html",
        {
            "form": form,
            "editing": True,
        },
    )



@role_required("ADMIN", "MANAGER", "HR")
def employee_delete(request, employee_id):
    employee = Employee.objects.get(id=employee_id)

    if request.method == "POST":
        employee.delete()
        return redirect("employee_list")

    return render(
        request,
        "hr/employee_confirm_delete.html",
        {"employee": employee},
    )