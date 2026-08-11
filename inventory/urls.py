from django.urls import path

from .views import (
    product_create,
    product_delete,
    product_list,
    product_update,
    stock_movement_create,
    stock_movement_history,
)

urlpatterns = [

    path(
        "",
        product_list,
        name="product_list",
    ),

    path(
        "add/",
        product_create,
        name="product_create",
    ),

    path(
        "<int:product_id>/edit/",
        product_update,
        name="product_update",
    ),

    path(
        "<int:product_id>/delete/",
        product_delete,
        name="product_delete",
    ),
    path(
        "stock-movement/",
        stock_movement_create,
        name="stock_movement_create",
    ),
    path(
        "stock-history/",
        stock_movement_history,
        name="stock_movement_history",
    ),

]