from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Expense
from .forms import ExpenseForm
from django.db.models import Q, Sum


@role_required("ADMIN", "MANAGER", "FINANCE")
def expense_list(request):

    today = timezone.localdate()

    total_paid = (
        Expense.objects.filter(
            status="PAID"
        ).aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    pending_count = Expense.objects.filter(
        status="PENDING"
    ).count()

    approved_amount = (
        Expense.objects.filter(
            status="APPROVED"
        ).aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    paid_this_month = (
        Expense.objects.filter(
            status="PAID",
            paid_at__year=today.year,
            paid_at__month=today.month,
        ).aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    expenses = Expense.objects.select_related(
        "created_by",
        "reviewed_by",
    ).order_by("-expense_date", "-id")

    search_query = request.GET.get(
        "q",
        "",
    ).strip()

    status_filter = request.GET.get(
        "status",
        "",
    )

    category_filter = request.GET.get(
        "category",
        "",
    )

    if search_query:
        expenses = expenses.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(reference_number__icontains=search_query)
        )

    if status_filter:
        expenses = expenses.filter(
            status=status_filter
        )

    if category_filter:
        expenses = expenses.filter(
            category=category_filter
        )

    context = {
        "expenses": expenses,
        "search_query": search_query,
        "status_filter": status_filter,
        "category_filter": category_filter,
        "status_choices": Expense.STATUS_CHOICES,
        "category_choices": Expense.CATEGORY_CHOICES,
        "total_paid": total_paid,
        "pending_count": pending_count,
        "approved_amount": approved_amount,
        "paid_this_month": paid_this_month,
    }

    return render(
        request,
        "finance/expense_list.html",
        context,
    )


@role_required("ADMIN", "MANAGER", "FINANCE")
def expense_create(request):

    if request.method == "POST":
        form = ExpenseForm(request.POST)

        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by = request.user
            expense.save()

            return redirect("expense_list")

    else:
        form = ExpenseForm()

    return render(
        request,
        "finance/expense_form.html",
        {
            "form": form,
        },
    )


@role_required("ADMIN", "MANAGER", "FINANCE")
def expense_edit(request, pk):

    expense = get_object_or_404(
        Expense,
        pk=pk,
    )

    if expense.status != "PENDING":
        return HttpResponseForbidden(
            "Only pending expenses can be edited."
        )

    if request.method == "POST":
        form = ExpenseForm(
            request.POST,
            instance=expense,
        )

        if form.is_valid():
            form.save()
            return redirect("expense_list")

    else:
        form = ExpenseForm(
            instance=expense,
        )

    return render(
        request,
        "finance/expense_form.html",
        {
            "form": form,
            "expense": expense,
        },
    )


@role_required("ADMIN", "MANAGER", "FINANCE")
def expense_delete(request, pk):

    expense = get_object_or_404(
        Expense,
        pk=pk,
    )

    if expense.status != "PENDING":
        return HttpResponseForbidden(
            "Only pending expenses can be deleted."
        )

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

@require_POST
@role_required("ADMIN", "MANAGER", "FINANCE")
def expense_approve(request, pk):

    expense = get_object_or_404(
        Expense,
        pk=pk,
    )

    if expense.status != "PENDING":
        return HttpResponseBadRequest(
            "Only pending expenses can be approved."
        )

    expense.status = "APPROVED"
    expense.reviewed_by = request.user
    expense.reviewed_at = timezone.now()

    expense.save(
        update_fields=[
            "status",
            "reviewed_by",
            "reviewed_at",
            "updated_at",
        ]
    )

    return redirect("expense_list")

@require_POST
@role_required("ADMIN", "MANAGER", "FINANCE")
def expense_reject(request, pk):

    expense = get_object_or_404(
        Expense,
        pk=pk,
    )

    if expense.status != "PENDING":
        return HttpResponseBadRequest(
            "Only pending expenses can be rejected."
        )

    expense.status = "REJECTED"
    expense.reviewed_by = request.user
    expense.reviewed_at = timezone.now()

    expense.save(
        update_fields=[
            "status",
            "reviewed_by",
            "reviewed_at",
            "updated_at",
        ]
    )

    return redirect("expense_list")

@require_POST
@role_required("ADMIN", "MANAGER", "FINANCE")
def expense_mark_paid(request, pk):

    expense = get_object_or_404(
        Expense,
        pk=pk,
    )

    if expense.status != "APPROVED":
        return HttpResponseBadRequest(
            "Only approved expenses can be marked as paid."
        )

    payment_method = request.POST.get("payment_method")

    valid_payment_methods = {
        choice[0]
        for choice in Expense.PAYMENT_METHOD_CHOICES
    }

    if payment_method not in valid_payment_methods:
        return HttpResponseBadRequest(
            "A valid payment method is required."
        )

    expense.status = "PAID"
    expense.payment_method = payment_method
    expense.paid_at = timezone.now()

    expense.save(
        update_fields=[
            "status",
            "payment_method",
            "paid_at",
            "updated_at",
        ]
    )

    return redirect("expense_list")