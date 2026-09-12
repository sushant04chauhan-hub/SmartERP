from django.contrib import messages
from decimal import Decimal
from inventory.models import Product
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import role_required

from .models import PurchaseOrder
from .services import (
    approve_purchase_order,
    cancel_purchase_order,
    mark_purchase_order_ordered,
    receive_purchase_order,
)
from .forms import (
    PurchaseOrderForm,
    PurchaseOrderItemFormSet,
)


def show_validation_error(request, error):

    if getattr(error, "messages", None):
        message = error.messages[0]
    else:
        message = str(error)

    messages.error(
        request,
        message,
    )


@role_required(
    "ADMIN",
    "MANAGER",
    "PROCUREMENT",
)

def purchase_order_create(request):

    purchase_order = PurchaseOrder()

    if request.method == "POST":

        form = PurchaseOrderForm(
            request.POST,
            instance=purchase_order,
        )

        formset = PurchaseOrderItemFormSet(
            request.POST,
            instance=purchase_order,
        )

        if form.is_valid() and formset.is_valid():

            with transaction.atomic():

                purchase_order = form.save(
                    commit=False
                )

                purchase_order.created_by = request.user
                purchase_order.status = "DRAFT"
                purchase_order.total_amount = Decimal(
                    "0.00"
                )

                purchase_order.save()

                formset.instance = purchase_order
                formset.save()

                total_amount = sum(
                    (
                        item.quantity * item.unit_price
                        for item
                        in purchase_order.items.all()
                    ),
                    Decimal("0.00"),
                )

                purchase_order.total_amount = total_amount

                purchase_order.save(
                    update_fields=[
                        "total_amount",
                        "updated_at",
                    ]
                )

            messages.success(
                request,
                "Purchase order created successfully.",
            )

            return redirect(
                "purchase_order_list"
            )

    else:

        form = PurchaseOrderForm(
            instance=purchase_order
        )

        formset = PurchaseOrderItemFormSet(
            instance=purchase_order
        )

    product_price_map = {
        str(product.id): (
            str(product.purchase_price)
            if product.purchase_price is not None
            else ""
        )
        for product in Product.objects.only(
            "id",
            "purchase_price",
        )
    }

    return render(
        request,
        "procurement/purchase_order_form.html",
        {
            "form": form,
            "formset": formset,
            "product_price_map": product_price_map,
        },
    )

@role_required(
    "ADMIN",
    "MANAGER",
    "PROCUREMENT",
)

def purchase_order_edit(request, purchase_order_id):

    purchase_order = get_object_or_404(
        PurchaseOrder,
        id=purchase_order_id,
    )

    if purchase_order.status != "DRAFT":

        messages.error(
            request,
            "Only draft purchase orders can be edited.",
        )

        return redirect(
            "purchase_order_list"
        )

    if request.method == "POST":

        form = PurchaseOrderForm(
            request.POST,
            instance=purchase_order,
        )

        formset = PurchaseOrderItemFormSet(
            request.POST,
            instance=purchase_order,
        )

        if form.is_valid() and formset.is_valid():

            with transaction.atomic():

                purchase_order = form.save()

                formset.save()

                total_amount = sum(
                    (
                        item.quantity * item.unit_price
                        for item
                        in purchase_order.items.all()
                    ),
                    Decimal("0.00"),
                )

                purchase_order.total_amount = total_amount

                purchase_order.save(
                    update_fields=[
                        "total_amount",
                        "updated_at",
                    ]
                )

            messages.success(
                request,
                "Purchase order updated successfully.",
            )

            return redirect(
                "purchase_order_list"
            )

    else:

        form = PurchaseOrderForm(
            instance=purchase_order,
        )

        formset = PurchaseOrderItemFormSet(
            instance=purchase_order,
        )

    product_price_map = {
        str(product.id): (
            str(product.purchase_price)
            if product.purchase_price is not None
            else ""
        )
        for product in Product.objects.only(
            "id",
            "purchase_price",
        )
    }

    return render(
        request,
        "procurement/purchase_order_form.html",
        {
            "form": form,
            "formset": formset,
            "product_price_map": product_price_map,
            "editing": True,
            "purchase_order": purchase_order,
        },
    )

def purchase_order_list(request):

    purchase_orders = (
        PurchaseOrder.objects
        .select_related(
            "supplier",
            "created_by",
            "approved_by",
        )
        .prefetch_related(
            "items__product"
        )
        .annotate(
            item_count=Count("items")
        )
        .order_by(
            "-order_date"
        )
    )

    profile = getattr(
        request.user,
        "profile",
        None,
    )

    role = getattr(
        profile,
        "role",
        None,
    )

    can_approve = (
        request.user.is_superuser
        or role in {
            "ADMIN",
            "MANAGER",
        }
    )

    return render(
        request,
        "procurement/purchase_order_list.html",
        {
            "purchase_orders": purchase_orders,
            "can_approve": can_approve,
        },
    )


@role_required(
    "ADMIN",
    "MANAGER",
)
@require_POST
def approve_purchase(request, purchase_order_id):

    purchase_order = get_object_or_404(
        PurchaseOrder,
        id=purchase_order_id,
    )

    try:

        approve_purchase_order(
            purchase_order=purchase_order,
            user=request.user,
        )

    except ValidationError as error:

        show_validation_error(
            request,
            error,
        )

    else:

        messages.success(
            request,
            "Purchase order approved successfully.",
        )

    return redirect(
        "purchase_order_list"
    )


@role_required(
    "ADMIN",
    "MANAGER",
    "PROCUREMENT",
)
@require_POST
def mark_purchase_order(request, purchase_order_id):

    purchase_order = get_object_or_404(
        PurchaseOrder,
        id=purchase_order_id,
    )

    try:

        mark_purchase_order_ordered(
            purchase_order=purchase_order,
        )

    except ValidationError as error:

        show_validation_error(
            request,
            error,
        )

    else:

        messages.success(
            request,
            "Purchase order marked as ordered.",
        )

    return redirect(
        "purchase_order_list"
    )


@role_required(
    "ADMIN",
    "MANAGER",
    "PROCUREMENT",
)
@require_POST
def receive_purchase(request, purchase_order_id):

    purchase_order = get_object_or_404(
        PurchaseOrder,
        id=purchase_order_id,
    )

    try:

        receive_purchase_order(
            purchase_order=purchase_order,
            user=request.user,
        )

    except ValidationError as error:

        show_validation_error(
            request,
            error,
        )

    else:

        messages.success(
            request,
            "Purchase order received successfully.",
        )

    return redirect(
        "purchase_order_list"
    )


@role_required(
    "ADMIN",
    "MANAGER",
    "PROCUREMENT",
)
@require_POST
def cancel_purchase(request, purchase_order_id):

    purchase_order = get_object_or_404(
        PurchaseOrder,
        id=purchase_order_id,
    )

    try:

        cancel_purchase_order(
            purchase_order=purchase_order,
        )

    except ValidationError as error:

        show_validation_error(
            request,
            error,
        )

    else:

        messages.success(
            request,
            "Purchase order cancelled.",
        )

    return redirect(
        "purchase_order_list"
    )