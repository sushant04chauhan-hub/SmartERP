from django.conf import settings
from django.db import models


class Product(models.Model):
    UNIT_CHOICES = [
        ("PCS", "Pieces"),
        ("BOX", "Box"),
        ("PACK", "Pack"),
        ("SET", "Set"),
    ]

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

    # Legacy field.
    # Existing values were migrated to purchase_price.
    # This field will be removed after all dependencies are updated.


    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    reorder_level = models.PositiveIntegerField(
        default=10
    )

    safety_stock = models.PositiveIntegerField(
        default=5
    )

    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        default="PCS"
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
        ("PURCHASE", "Purchase"),
        ("SALE", "Sale"),
        ("RETURN_IN", "Return In"),
        ("RETURN_OUT", "Return Out"),
        ("ADJUSTMENT_IN", "Adjustment In"),
        ("ADJUSTMENT_OUT", "Adjustment Out"),
        ("DAMAGED", "Damaged"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stock_movements"
    )

    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_CHOICES
    )

    quantity = models.PositiveIntegerField()

    reference = models.CharField(
        max_length=100,
        blank=True
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements_created"
    )

    note = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product.name} - {self.movement_type} - {self.quantity}"