from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils import timezone

from .models import (
    PurchaseOrder,
    PurchaseOrderItem,
    Supplier,
)


class PurchaseOrderForm(forms.ModelForm):

    class Meta:
        model = PurchaseOrder

        fields = [
            "order_number",
            "supplier",
            "expected_delivery_date",
            "notes",
        ]

        widgets = {
            "expected_delivery_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Optional purchase order notes",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["supplier"].queryset = (
            Supplier.objects
            .filter(is_active=True)
            .order_by("name")
        )

    def clean_expected_delivery_date(self):

        expected_date = self.cleaned_data.get(
            "expected_delivery_date"
        )

        if (
            expected_date
            and expected_date < timezone.localdate()
        ):
            raise forms.ValidationError(
                "Expected delivery date cannot be in the past."
            )

        return expected_date

class PurchaseOrderItemForm(forms.ModelForm):

    class Meta:
        model = PurchaseOrderItem

        fields = [
            "product",
            "quantity",
            "unit_price",
        ]

    def clean_quantity(self):

        quantity = self.cleaned_data.get(
            "quantity"
        )

        if quantity is not None and quantity <= 0:
            raise forms.ValidationError(
                "Quantity must be greater than zero."
            )

        return quantity

    def clean_unit_price(self):

        unit_price = self.cleaned_data.get(
            "unit_price"
        )

        if unit_price is not None and unit_price <= 0:
            raise forms.ValidationError(
                "Unit price must be greater than zero."
            )

        return unit_price

class BasePurchaseOrderItemFormSet(
    BaseInlineFormSet
):

    def clean(self):

        super().clean()

        if any(self.errors):
            return

        products = set()

        for form in self.forms:

            if not hasattr(
                form,
                "cleaned_data",
            ):
                continue

            if form.cleaned_data.get(
                "DELETE",
                False,
            ):
                continue

            product = form.cleaned_data.get(
                "product"
            )

            if product is None:
                continue

            if product.pk in products:
                raise forms.ValidationError(
                    "The same product cannot be added "
                    "more than once to a purchase order."
                )

            products.add(
                product.pk
            )

PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    formset=BasePurchaseOrderItemFormSet,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True,
)