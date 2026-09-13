from django.urls import path

from .views import (
    expense_approve,
    expense_create,
    expense_delete,
    expense_edit,
    expense_list,
    expense_mark_paid,
    expense_reject,
)


urlpatterns = [
    path(
        "",
        expense_list,
        name="expense_list",
    ),

    path(
        "add/",
        expense_create,
        name="expense_create",
    ),
    path(
        "<int:pk>/edit/",
        expense_edit,
        name="expense_edit",
    ),

    path(
        "<int:pk>/delete/",
        expense_delete,
        name="expense_delete",
    ),

    path(
        "<int:pk>/approve/",
        expense_approve,
        name="expense_approve",
    ),

    path(
        "<int:pk>/reject/",
        expense_reject,
        name="expense_reject",
    ),

    path(
        "<int:pk>/mark-paid/",
        expense_mark_paid,
        name="expense_mark_paid",
    ),
]
