from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Product, StockMovement
from .services import apply_stock_movement


class InventoryServiceTests(TestCase):

    def setUp(self):

        self.user = get_user_model().objects.create_user(
            username="inventory_test_user",
            password="test-password-123",
        )

        self.product = Product.objects.create(
            product_code="TEST-P001",
            name="Test Product",
            category="Testing",
            description="Product used for automated tests",
            quantity=10,
            purchase_price=100,
            selling_price=150,
            reorder_level=5,
            safety_stock=2,
            unit="PCS",
        )

    def test_adjustment_in_increases_stock(self):

        product, movement = apply_stock_movement(
            product=self.product,
            movement_type="ADJUSTMENT_IN",
            quantity=5,
            user=self.user,
            reference="TEST-IN",
            note="Automated test",
        )

        product.refresh_from_db()

        self.assertEqual(
            product.quantity,
            15,
        )

        self.assertEqual(
            movement.movement_type,
            "ADJUSTMENT_IN",
        )

        self.assertEqual(
            movement.quantity,
            5,
        )

        self.assertEqual(
            movement.reference,
            "TEST-IN",
        )

        self.assertEqual(
            movement.created_by,
            self.user,
        )

    def test_adjustment_out_decreases_stock(self):

        product, movement = apply_stock_movement(
            product=self.product,
            movement_type="ADJUSTMENT_OUT",
            quantity=4,
            user=self.user,
            reference="TEST-OUT",
            note="Automated test",
        )

        product.refresh_from_db()

        self.assertEqual(
            product.quantity,
            6,
        )

        self.assertEqual(
            movement.movement_type,
            "ADJUSTMENT_OUT",
        )

    def test_insufficient_stock_is_rejected(self):

        with self.assertRaises(ValidationError):

            apply_stock_movement(
                product=self.product,
                movement_type="ADJUSTMENT_OUT",
                quantity=100,
                user=self.user,
            )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.quantity,
            10,
        )

        self.assertEqual(
            StockMovement.objects.count(),
            0,
        )

    def test_zero_quantity_is_rejected(self):

        with self.assertRaises(ValidationError):

            apply_stock_movement(
                product=self.product,
                movement_type="ADJUSTMENT_IN",
                quantity=0,
                user=self.user,
            )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.quantity,
            10,
        )

        self.assertEqual(
            StockMovement.objects.count(),
            0,
        )