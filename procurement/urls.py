from django.urls import path

from .views import (
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
        "<int:purchase_order_id>/receive/",
        receive_purchase,
        name="receive_purchase",
    ),

]