from django.contrib import admin

from .models import Supplier, PurchaseOrder, PurchaseOrderItem


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "contact_person",
        "email",
        "phone",
        "created_at",
    )

    search_fields = (
        "name",
        "contact_person",
        "email",
        "phone",
    )

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_number",
        "supplier",
        "order_date",
        "status",
        "total_amount",
    )

    list_filter = (
        "status",
        "order_date",
    )

    search_fields = (
        "order_number",
        "supplier__name",
    )

@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "purchase_order",
        "product",
        "quantity",
        "unit_price",
        "total_price",
    )

    list_filter = (
        "purchase_order",
        "product",
    )

    search_fields = (
        "purchase_order__order_number",
        "product__name",
        "product__product_code",
    )