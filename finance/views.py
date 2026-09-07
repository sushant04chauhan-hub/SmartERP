from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from django.shortcuts import redirect, render, get_object_or_404

from .models import Expense


@role_required("ADMIN", "MANAGER", "FINANCE")
def expense_list(request):

    expenses = Expense.objects.all().order_by(
        "-expense_date"
    )

    return render(
        request,
        "finance/expense_list.html",
        {
            "expenses": expenses,
        },
    )


@role_required("ADMIN", "MANAGER", "FINANCE")
def expense_create(request):

    if request.method == "POST":

        Expense.objects.create(
            title=request.POST.get("title"),
            category=request.POST.get("category"),
            amount=request.POST.get("amount"),
            expense_date=request.POST.get("expense_date"),
            description=request.POST.get("description"),
        )

        return redirect("expense_list")

    return render(
        request,
        "finance/expense_form.html",
    )


@role_required("ADMIN", "MANAGER", "FINANCE")
def expense_edit(request, pk):

    expense = get_object_or_404(Expense, pk=pk)

    if request.method == "POST":

        expense.title = request.POST.get("title")
        expense.category = request.POST.get("category")
        expense.amount = request.POST.get("amount")
        expense.expense_date = request.POST.get("expense_date")
        expense.description = request.POST.get("description")

        expense.save()

        return redirect("expense_list")

    return render(
        request,
        "finance/expense_form.html",
        {
            "expense": expense,
        },
    )


@role_required("ADMIN", "MANAGER", "FINANCE")
def expense_delete(request, pk):

    expense = get_object_or_404(Expense, pk=pk)

    if request.method == "POST":
        expense.delete()
        return redirect("expense_list")

    return render(
        request,
        "finance/expense_confirm_delete.html",
        {
            "expense": expense,
        },
    )