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

class StockMovement(models.Model):

    MOVEMENT_CHOICES = [
        ("IN", "Stock In"),
        ("OUT", "Stock Out"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stock_movements"
    )

    movement_type = models.CharField(
        max_length=3,
        choices=MOVEMENT_CHOICES
    )

    quantity = models.PositiveIntegerField()

    note = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product.name} - {self.movement_type} - {self.quantity}"