from django.urls import path

from .views import (
    cancel_order,
    complete_order,
    confirm_order,
    customer_create,
    customer_edit,
    customer_list,
    customer_toggle_status,
    sales_order_create,
    sales_order_edit,
    sales_order_list,
)

urlpatterns = [

    path(
        "customers/",
        customer_list,
        name="customer_list",
    ),

    path(
        "<int:sales_order_id>/complete/",
        complete_order,
        name="complete_order",
    ),

    path(
        "customers/create/",
        customer_create,
        name="customer_create",
    ),

    path(
        "customers/<int:customer_id>/edit/",
        customer_edit,
        name="customer_edit",
    ),

    path(
        "customers/<int:customer_id>/toggle-status/",
        customer_toggle_status,
        name="customer_toggle_status",
    ),

    path(
        "",
        sales_order_list,
        name="sales_order_list",
    ),

    path(
        "create/",
        sales_order_create,
        name="sales_order_create",
    ),

    path(
        "<int:sales_order_id>/edit/",
        sales_order_edit,
        name="sales_order_edit",
    ),

    path(
        "<int:sales_order_id>/confirm/",
        confirm_order,
        name="confirm_order",
    ),
    
    path(
        "<int:sales_order_id>/cancel/",
        cancel_order,
        name="cancel_order",
    ),
]