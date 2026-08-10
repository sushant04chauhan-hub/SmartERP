from django import forms

from .models import Employee


class EmployeeForm(forms.ModelForm):

    class Meta:
        model = Employee

        fields = [
            "employee_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "department",
            "designation",
            "joining_date",
            "salary",
            "status",
        ]

        widgets = {
            "joining_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }