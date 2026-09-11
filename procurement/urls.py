from django.urls import path

from .views import (
    approve_purchase,
    cancel_purchase,
    mark_purchase_order,
    purchase_order_list,
    receive_purchase,
)


urlpatterns = [

    path(
        "",
        purchase_order_list,
        name="purchase_order_list",
    ),

    path(
        "<int:purchase_order_id>/approve/",
        approve_purchase,
        name="approve_purchase",
    ),

    path(
        "<int:purchase_order_id>/order/",
        mark_purchase_order,
        name="mark_purchase_order",
    ),

    path(
        "<int:purchase_order_id>/receive/",
        receive_purchase,
        name="receive_purchase",
    ),

    path(
        "<int:purchase_order_id>/cancel/",
        cancel_purchase,
        name="cancel_purchase",
    ),

]