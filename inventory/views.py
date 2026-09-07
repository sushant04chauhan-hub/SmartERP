from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from django.db import models, transaction
from django.shortcuts import redirect, render

from .forms import ProductForm, StockMovementForm
from .models import Product, StockMovement


@role_required("ADMIN", "MANAGER", "INVENTORY")
def product_list(request):

    products = Product.objects.all().order_by("name")

    search = request.GET.get("search", "").strip()
    category = request.GET.get("category", "").strip()
    stock_status = request.GET.get("stock_status", "").strip()

    if search:
        products = products.filter(
            product_code__icontains=search
        ) | products.filter(
            name__icontains=search
        ) | products.filter(
            category__icontains=search
        )

    if category:
        products = products.filter(
            category=category
        )

    if stock_status == "LOW":
        products = products.filter(
            quantity__lte=models.F("reorder_level")
        )

    elif stock_status == "IN_STOCK":
        products = products.filter(
            quantity__gt=models.F("reorder_level")
        )

    products = products.distinct()

    categories = (
        Product.objects
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )

    return render(
        request,
        "inventory/product_list.html",
        {
            "products": products,
            "categories": categories,
            "search": search,
            "selected_category": category,
            "selected_stock_status": stock_status,
            "product_count": products.count(),
        },
    )
@role_required("ADMIN", "MANAGER", "INVENTORY")
def product_create(request):

    if request.method == "POST":

        form = ProductForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect("product_list")

    else:

        form = ProductForm()

    return render(
        request,
        "inventory/product_form.html",
        {
            "form": form,
        },
    )

@role_required("ADMIN", "MANAGER", "INVENTORY")
def product_update(request, product_id):

    product = Product.objects.get(id=product_id)

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            instance=product
        )

        if form.is_valid():
            form.save()

            return redirect("product_list")

    else:

        form = ProductForm(
            instance=product
        )

    return render(
        request,
        "inventory/product_form.html",
        {
            "form": form,
            "editing": True,
        },
    )


@role_required("ADMIN", "MANAGER", "INVENTORY")
def product_delete(request, product_id):

    product = Product.objects.get(id=product_id)

    if request.method == "POST":

        product.delete()

        return redirect("product_list")

    return render(
        request,
        "inventory/product_confirm_delete.html",
        {
            "product": product,
        },
    )

@role_required("ADMIN", "MANAGER", "INVENTORY")
def stock_movement_create(request):

    if request.method == "POST":

        form = StockMovementForm(request.POST)

        if form.is_valid():

            movement = form.save(commit=False)

            product = movement.product

            if movement.movement_type == "OUT":

                if movement.quantity > product.quantity:

                    form.add_error(
                        "quantity",
                        "Stock Out quantity cannot be greater than current stock."
                    )

                else:

                    with transaction.atomic():

                        product.quantity -= movement.quantity
                        product.save()

                        movement.save()

                    return redirect("product_list")

            else:

                with transaction.atomic():

                    product.quantity += movement.quantity
                    product.save()

                    movement.save()

                return redirect("product_list")

    else:

        form = StockMovementForm()

    return render(
        request,
        "inventory/stock_movement_form.html",
        {
            "form": form,
        },
    )

@role_required("ADMIN", "MANAGER", "INVENTORY")
def stock_movement_history(request):

    movements = StockMovement.objects.select_related(
        "product"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "inventory/stock_movement_history.html",
        {
            "movements": movements,
        },
    )