from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Expense


@login_required
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