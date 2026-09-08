from django.contrib import messages
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from inventory.services import apply_stock_movement

from .models import PurchaseOrder

@role_required(
    "ADMIN",
    "MANAGER",
    "PROCUREMENT",
)
@transaction.atomic
def receive_purchase(request, purchase_order_id):

    purchase_order = get_object_or_404(
        PurchaseOrder.objects.prefetch_related(
            "items__product"
        ),
        id=purchase_order_id,
    )

    if request.method != "POST":
        return redirect("purchase_order_list")

    if purchase_order.status == "RECEIVED":
        messages.error(
            request,
            "This purchase order has already been received.",
        )
        return redirect("purchase_order_list")

    if purchase_order.status != "PENDING":
        messages.error(
            request,
            "Only pending purchase orders can be received.",
        )
        return redirect("purchase_order_list")

    for item in purchase_order.items.all():

        apply_stock_movement(
            product=item.product,
            movement_type="PURCHASE",
            quantity=item.quantity,
            user=request.user,
            reference=purchase_order.order_number,
            note="Stock received from purchase order",
        )

    purchase_order.status = "RECEIVED"

    purchase_order.save(
        update_fields=["status"]
    )

    messages.success(
        request,
        "Purchase order received successfully.",
    )

    return redirect("purchase_order_list")

@role_required("ADMIN","MANAGER","PROCUREMENT",)
def purchase_order_list(request):

    purchase_orders = PurchaseOrder.objects.select_related(
        "supplier"
    ).prefetch_related(
        "items__product"
    ).annotate(
        item_count=Count("items")
    ).order_by(
        "-order_date"
    )

    return render(
        request,
        "procurement/purchase_order_list.html",
        {
            "purchase_orders": purchase_orders,
        },
    )