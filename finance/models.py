from django.db import models

class Expense(models.Model):

    CATEGORY_CHOICES = [
        ("OFFICE", "Office"),
        ("UTILITIES", "Utilities"),
        ("TRAVEL", "Travel"),
        ("MAINTENANCE", "Maintenance"),
        ("SALARY", "Salary"),
        ("OTHER", "Other"),
    ]

    title = models.CharField(
        max_length=150
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    expense_date = models.DateField()

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.title} - ₹{self.amount}"
