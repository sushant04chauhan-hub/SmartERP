from django import forms
from django.forms import (
    BaseInlineFormSet,
    inlineformset_factory,
)

from .models import (
    Customer,
    SalesOrder,
    SalesOrderItem,
)


class CustomerForm(forms.ModelForm):

    class Meta:

        model = Customer

        fields = [
            "name",
            "email",
            "phone",
            "address",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Customer name"
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Email address"
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "placeholder": "Phone number"
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Customer address"
                }
            ),
        }


class SalesOrderForm(forms.ModelForm):

    class Meta:

        model = SalesOrder

        fields = [
            "order_number",
            "customer",
            "notes",
        ]

        widgets = {
            "notes": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(
            *args,
            **kwargs
        )

        self.fields[
            "customer"
        ].queryset = Customer.objects.filter(
            is_active=True
        ).order_by(
            "name"
        )


class SalesOrderItemForm(forms.ModelForm):

    class Meta:

        model = SalesOrderItem

        fields = [
            "product",
            "quantity",
            "unit_price",
        ]

    def clean_quantity(self):

        quantity = self.cleaned_data[
            "quantity"
        ]

        if quantity <= 0:

            raise forms.ValidationError(
                "Quantity must be greater than zero."
            )

        return quantity

    def clean_unit_price(self):

        unit_price = self.cleaned_data[
            "unit_price"
        ]

        if unit_price <= 0:

            raise forms.ValidationError(
                "Unit price must be greater than zero."
            )

        return unit_price


class BaseSalesOrderItemFormSet(
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
                "cleaned_data"
            ):
                continue

            if form.cleaned_data.get(
                "DELETE"
            ):
                continue

            product = form.cleaned_data.get(
                "product"
            )

            if product is None:
                continue

            if product.id in products:

                raise forms.ValidationError(
                    "The same product cannot be added "
                    "more than once to a sales order."
                )

            products.add(
                product.id
            )


class CustomerForm(forms.ModelForm):

    class Meta:

        model = Customer

        fields = [
            "name",
            "email",
            "phone",
            "address",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Customer name"
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Email address"
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "placeholder": "Phone number"
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Customer address"
                }
            ),
        }

SalesOrderItemFormSet = (
    inlineformset_factory(
        SalesOrder,
        SalesOrderItem,
        form=SalesOrderItemForm,
        formset=BaseSalesOrderItemFormSet,
        extra=1,
        min_num=1,
        validate_min=True,
        can_delete=True,
    )
)
