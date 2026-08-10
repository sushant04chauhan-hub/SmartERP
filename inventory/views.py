from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProductForm
from .models import Product

@login_required
def product_list(request):

    products = Product.objects.all().order_by("name")

    return render(
        request,
        "inventory/product_list.html",
        {
            "products": products,
        },
    )

@login_required
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

@login_required
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


@login_required
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