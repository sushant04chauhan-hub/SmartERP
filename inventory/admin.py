from django.contrib import admin

from .models import Product, StockMovement


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "product_code",
        "name",
        "category",
        "quantity",
        "unit_price",
        "reorder_level",
    )

    list_filter = (
        "category",
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