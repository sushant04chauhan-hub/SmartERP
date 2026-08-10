from django.urls import path

from .views import (
    product_create,
    product_delete,
    product_list,
    product_update,
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

]