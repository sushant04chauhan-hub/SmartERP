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
            "purchase_price",
            "selling_price",
            "reorder_level",
            "safety_stock",
            "unit",
        ]

        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                }
            ),
        }

class StockMovementForm(forms.ModelForm):

    movement_type = forms.ChoiceField(
        choices=[
            ("ADJUSTMENT_IN", "Adjustment In"),
            ("ADJUSTMENT_OUT", "Adjustment Out"),
        ],
        label="Adjustment Type",
    )

    class Meta:
        model = StockMovement

        fields = [
            "product",
            "movement_type",
            "quantity",
            "reference",
            "note",
        ]

        widgets = {
            "reference": forms.TextInput(
                attrs={
                    "placeholder": "Optional reference",
                }
            ),
            "note": forms.TextInput(
                attrs={
                    "placeholder": "Reason for adjustment",
                }
            ),
        }