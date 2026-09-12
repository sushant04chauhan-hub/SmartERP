from django.core.exceptions import ValidationError
from inventory.models import Product
from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.http import require_POST

from accounts.decorators import role_required

from .forms import (
    CustomerForm,
    SalesOrderForm,
    SalesOrderItemFormSet,
)
from .models import (
    Customer,
    SalesOrder,
    SalesOrderItem,
)

from .services import (
    cancel_sales_order,
    complete_sales_order,
    confirm_sales_order,
)

@role_required(
    "ADMIN",
    "MANAGER",
    "SALES",
)
def customer_list(request):

    customers = Customer.objects.all().order_by(
        "name"
    )

    return render(
        request,
        "sales/customer_list.html",
        {
            "customers": customers,
        },
    )


@role_required(
    "ADMIN",
    "MANAGER",
    "SALES",
)
def customer_create(request):

    if request.method == "POST":

        form = CustomerForm(
            request.POST
        )

        if form.is_valid():

            customer = form.save()

            messages.success(
                request,
                (
                    f"Customer "
                    f"{customer.name} "
                    f"created successfully."
                ),
            )

            return redirect(
                "customer_list"
            )

    else:

        form = CustomerForm()

    return render(
        request,
        "sales/customer_form.html",
        {
            "form": form,
            "editing": False,
        },
    )


@role_required(
    "ADMIN",
    "MANAGER",
    "SALES",
)
def customer_edit(
    request,
    customer_id,
):

    customer = get_object_or_404(
        Customer,
        id=customer_id,
    )

    if request.method == "POST":

        form = CustomerForm(
            request.POST,
            instance=customer,
        )

        if form.is_valid():

            customer = form.save()

            messages.success(
                request,
                (
                    f"Customer "
                    f"{customer.name} "
                    f"updated successfully."
                ),
            )

            return redirect(
                "customer_list"
            )

    else:

        form = CustomerForm(
            instance=customer
        )

    return render(
        request,
        "sales/customer_form.html",
        {
            "form": form,
            "editing": True,
            "customer": customer,
        },
    )


@require_POST
@role_required(
    "ADMIN",
    "MANAGER",
    "SALES",
)
def customer_toggle_status(
    request,
    customer_id,
):

    customer = get_object_or_404(
        Customer,
        id=customer_id,
    )

    customer.is_active = (
        not customer.is_active
    )

    customer.save(
        update_fields=[
            "is_active",
            "updated_at",
        ]
    )

    if customer.is_active:

        messages.success(
            request,
            (
                f"{customer.name} "
                f"has been activated."
            ),
        )

    else:

        messages.success(
            request,
            (
                f"{customer.name} "
                f"has been deactivated."
            ),
        )

    return redirect(
        "customer_list"
    )

@role_required(
    "ADMIN",
    "MANAGER",
    "SALES",
)
def sales_order_list(request):

    search_query = request.GET.get(
        "q",
        "",
    ).strip()

    status_filter = request.GET.get(
        "status",
        "",
    ).strip()

    sales_orders = (
        SalesOrder.objects
        .select_related(
            "customer",
            "created_by",
        )
        .annotate(
            item_count=Count(
                "items"
            )
        )
    )

    if search_query:

        sales_orders = sales_orders.filter(
            Q(
                order_number__icontains=
                    search_query
            )
            |
            Q(
                customer__name__icontains=
                    search_query
            )
        )

    valid_statuses = {
        "DRAFT",
        "CONFIRMED",
        "COMPLETED",
        "CANCELLED",
    }

    if status_filter in valid_statuses:

        sales_orders = sales_orders.filter(
            status=status_filter
        )

    sales_orders = sales_orders.order_by(
        "-created_at"
    )

    completed_orders = (
        SalesOrder.objects.filter(
            status="COMPLETED"
        )
    )

    total_orders = (
        SalesOrder.objects.count()
    )

    completed_order_count = (
        completed_orders.count()
    )

    completed_revenue = (
        completed_orders.aggregate(
            total=Sum(
                "total_amount"
            )
        )["total"]
        or Decimal("0.00")
    )

    units_sold = (
        SalesOrderItem.objects.filter(
            sales_order__status="COMPLETED"
        )
        .aggregate(
            total=Sum(
                "quantity"
            )
        )["total"]
        or 0
    )

    return render(
        request,
        "sales/sales_order_list.html",
        {
            "sales_orders":
                sales_orders,

            "total_orders":
                total_orders,

            "completed_order_count":
                completed_order_count,

            "completed_revenue":
                completed_revenue,

            "units_sold":
                units_sold,

            "search_query":
                search_query,

            "status_filter":
                status_filter,
        },
    )

@role_required(
    "ADMIN",
    "MANAGER",
    "SALES",
)
def sales_order_create(request):

    sales_order = SalesOrder()

    if request.method == "POST":

        form = SalesOrderForm(
            request.POST,
            instance=sales_order,
        )

        formset = SalesOrderItemFormSet(
            request.POST,
            instance=sales_order,
        )

        if (
            form.is_valid()
            and formset.is_valid()
        ):

            with transaction.atomic():

                sales_order = form.save(
                    commit=False
                )

                sales_order.created_by = (
                    request.user
                )

                sales_order.status = (
                    "DRAFT"
                )

                sales_order.total_amount = (
                    Decimal("0.00")
                )

                sales_order.save()

                formset.instance = (
                    sales_order
                )

                formset.save()

                total_amount = sum(
                    (
                        item.quantity
                        * item.unit_price

                        for item
                        in sales_order.items.all()
                    ),
                    Decimal("0.00"),
                )

                sales_order.total_amount = (
                    total_amount
                )

                sales_order.save(
                    update_fields=[
                        "total_amount",
                        "updated_at",
                    ]
                )

            messages.success(
                request,
                "Sales order created successfully.",
            )

            return redirect(
                "sales_order_list"
            )

    else:

        form = SalesOrderForm(
            instance=sales_order
        )

        formset = SalesOrderItemFormSet(
            instance=sales_order
        )

    product_price_map = {
        str(product.id): (
            str(product.selling_price)
            if product.selling_price is not None
            else ""
        )
        for product in Product.objects.only(
            "id",
            "selling_price",
        )
    }

    return render(
        request,
        "sales/sales_order_form.html",
        {
            "form": form,
            "formset": formset,
            "product_price_map": product_price_map,
            "editing": False,
        },
    )

@role_required(
    "ADMIN",
    "MANAGER",
    "SALES",
)
def sales_order_edit(
    request,
    sales_order_id,
):

    sales_order = get_object_or_404(
        SalesOrder,
        id=sales_order_id,
    )

    if sales_order.status != "DRAFT":

        messages.error(
            request,
            "Only draft sales orders can be edited.",
        )

        return redirect(
            "sales_order_list"
        )

    if request.method == "POST":

        form = SalesOrderForm(
            request.POST,
            instance=sales_order,
        )

        formset = SalesOrderItemFormSet(
            request.POST,
            instance=sales_order,
        )

        if (
            form.is_valid()
            and formset.is_valid()
        ):

            with transaction.atomic():

                sales_order = form.save()

                formset.save()

                total_amount = sum(
                    (
                        item.quantity
                        * item.unit_price

                        for item
                        in sales_order.items.all()
                    ),
                    Decimal("0.00"),
                )

                sales_order.total_amount = (
                    total_amount
                )

                sales_order.save(
                    update_fields=[
                        "total_amount",
                        "updated_at",
                    ]
                )

            messages.success(
                request,
                "Sales order updated successfully.",
            )

            return redirect(
                "sales_order_list"
            )

    else:

        form = SalesOrderForm(
            instance=sales_order
        )

        formset = SalesOrderItemFormSet(
            instance=sales_order
        )

    product_price_map = {
        str(product.id): (
            str(product.selling_price)
            if product.selling_price is not None
            else ""
        )
        for product in Product.objects.only(
            "id",
            "selling_price",
        )
    }

    return render(
        request,
        "sales/sales_order_form.html",
        {
            "form": form,
            "formset": formset,
            "product_price_map":
                product_price_map,
            "editing": True,
            "sales_order": sales_order,
        },
    )
@require_POST
@role_required(
    "ADMIN",
    "MANAGER",
    "SALES",
)
def confirm_order(
    request,
    sales_order_id,
):

    sales_order = get_object_or_404(
        SalesOrder,
        id=sales_order_id,
    )

    try:

        confirm_sales_order(
            sales_order=sales_order
        )

        messages.success(
            request,
            "Sales order confirmed successfully.",
        )

    except ValidationError as error:

        messages.error(
            request,
            error.messages[0],
        )

    return redirect(
        "sales_order_list"
    )

@require_POST
@role_required(
    "ADMIN",
    "MANAGER",
    "SALES",
)
def cancel_order(
    request,
    sales_order_id,
):

    sales_order = get_object_or_404(
        SalesOrder,
        id=sales_order_id,
    )

    try:

        cancel_sales_order(
            sales_order=sales_order
        )

        messages.success(
            request,
            "Sales order cancelled successfully.",
        )

    except ValidationError as error:

        messages.error(
            request,
            error.messages[0],
        )

    return redirect(
        "sales_order_list"
    )

@require_POST
@role_required(
    "ADMIN",
    "MANAGER",
    "SALES",
)
def complete_order(
    request,
    sales_order_id,
):

    sales_order = get_object_or_404(
        SalesOrder,
        id=sales_order_id,
    )

    try:

        complete_sales_order(
            sales_order=sales_order,
            user=request.user,
        )

        messages.success(
            request,
            "Sales order completed successfully.",
        )

    except ValidationError as error:

        messages.error(
            request,
            error.messages[0],
        )

    return redirect(
        "sales_order_list"
    )