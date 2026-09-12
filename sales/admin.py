from django.contrib import admin

from .models import (
    Customer,
    SalesOrder,
    SalesOrderItem,
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "email",
        "phone",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "email",
        "phone",
    )


class SalesOrderItemInline(admin.TabularInline):

    model = SalesOrderItem

    extra = 0


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_number",
        "customer",
        "status",
        "total_amount",
        "order_date",
        "completed_date",
        "created_by",
    )

    list_filter = (
        "status",
        "order_date",
    )

    search_fields = (
        "order_number",
        "customer__name",
    )

    inlines = [
        SalesOrderItemInline,
    ]


@admin.register(SalesOrderItem)
class SalesOrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "sales_order",
        "product",
        "quantity",
        "unit_price",
        "total_price",
    )

    search_fields = (
        "sales_order__order_number",
        "product__name",
        "product__product_code",
    )