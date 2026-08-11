from django import forms

from .models import Product, StockMovement


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

class StockMovementForm(forms.ModelForm):

    class Meta:
        model = StockMovement

        fields = [
            "product",
            "movement_type",
            "quantity",
            "note",
        ]

        widgets = {
            "note": forms.TextInput(
                attrs={
                    "placeholder": "Optional note",
                }
            ),
        }