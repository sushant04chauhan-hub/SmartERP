from django import forms

from .models import Expense


class ExpenseForm(forms.ModelForm):

    class Meta:
        model = Expense

        fields = [
            "title",
            "category",
            "amount",
            "expense_date",
            "reference_number",
            "description",
        ]

        widgets = {
            "expense_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "description": forms.Textarea(
                attrs={"rows": 4}
            ),
        }

    def clean_amount(self):
        amount = self.cleaned_data["amount"]

        if amount <= 0:
            raise forms.ValidationError(
                "Expense amount must be greater than zero."
            )

        return amount