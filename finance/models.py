from django.conf import settings
from django.db import models


class Expense(models.Model):

    CATEGORY_CHOICES = [
        ("OFFICE", "Office"),
        ("UTILITIES", "Utilities"),
        ("TRAVEL", "Travel"),
        ("MAINTENANCE", "Maintenance"),
        ("SALARY", "Salary"),
        ("PROCUREMENT", "Procurement"),
        ("OTHER", "Other"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("PAID", "Paid"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("CASH", "Cash"),
        ("BANK_TRANSFER", "Bank Transfer"),
        ("UPI", "UPI"),
        ("CARD", "Card"),
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

    reference_number = models.CharField(
        max_length=100,
        blank=True
    )

    purchase_order = models.OneToOneField(
        "procurement.PurchaseOrder",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="finance_expense",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_expenses"
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_expenses"
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    paid_at = models.DateTimeField(
        null=True,
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

class Revenue(models.Model):

    sales_order = models.OneToOneField(
        "sales.SalesOrder",
        on_delete=models.PROTECT,
        related_name="finance_revenue",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    revenue_date = models.DateField()

    reference_number = models.CharField(
        max_length=100,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_revenues",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.reference_number} - "
            f"₹{self.amount}"
        )