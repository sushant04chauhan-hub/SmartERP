from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .models import PurchaseOrder
from inventory.models import StockMovement

@login_required
def receive_purchase(request, purchase_order_id):

    purchase_order = get_object_or_404(
        PurchaseOrder,
        id=purchase_order_id
    )

    if request.method == "POST":

        if purchase_order.status != "PENDING":
            return redirect("purchase_order_list")

        with transaction.atomic():

            for item in purchase_order.items.select_related("product"):

                product = item.product

                product.quantity += item.quantity

                product.save()

                StockMovement.objects.create(
                    product=product,
                    movement_type="IN",
                    quantity=item.quantity,
                    note=f"Purchase Order {purchase_order.order_number}",
                )

            purchase_order.status = "RECEIVED"

            purchase_order.save()

        return redirect("purchase_order_list")

    return redirect("purchase_order_list")

@login_required
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