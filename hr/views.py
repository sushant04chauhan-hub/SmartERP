from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import EmployeeForm
from .models import Employee


@login_required
def employee_list(request):
    employees = Employee.objects.select_related("department").all()

    return render(
        request,
        "hr/employee_list.html",
        {"employees": employees},
    )


@login_required
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


@login_required
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

@login_required
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