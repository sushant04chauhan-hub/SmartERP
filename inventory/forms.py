from django import forms

from .models import Product


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product

        fields = [
            "product_code",
            "name",
            "category",
            "description",
            "quantity",
            "unit_price",
            "reorder_level",
        ]

        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                }
            ),
        }