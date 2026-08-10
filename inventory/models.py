from django.db import models


class Product(models.Model):

    product_code = models.CharField(
        max_length=50,
        unique=True
    )

    name = models.CharField(
        max_length=150
    )

    category = models.CharField(
        max_length=100
    )

    description = models.TextField(
        blank=True
    )

    quantity = models.PositiveIntegerField(
        default=0
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    reorder_level = models.PositiveIntegerField(
        default=10
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.product_code} - {self.name}"