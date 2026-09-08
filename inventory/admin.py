from django.contrib import admin

from .models import Product, StockMovement


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "product_code",
        "name",
        "category",
        "quantity",
        "purchase_price",
        "selling_price",
        "reorder_level",
        "safety_stock",
        "unit",
    )

    list_filter = (
        "category",
        "unit",
    )

    search_fields = (
        "product_code",
        "name",
    )


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "movement_type",
        "quantity",
        "note",
        "created_at",
    )

    list_filter = (
        "movement_type",
        "created_at",
    )

    search_fields = (
        "product__name",
        "product__product_code",
        "note",
    )

    readonly_fields = (
        "created_at",
    )