from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from inventory.models import Product, StockMovement

from .models import (
    PurchaseOrder,
    PurchaseOrderItem,
    Supplier,
)


class PurchaseReceivingTests(TestCase):

    def setUp(self):

        self.user = get_user_model().objects.create_user(
            username="procurement_test_user",
            password="test-password-123",
        )

        self.user.profile.role = "PROCUREMENT"
        self.user.profile.save()

        self.client.force_login(
            self.user
        )

        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            contact_person="Test Contact",
            email="supplier@example.com",
        )

        self.product = Product.objects.create(
            product_code="PROC-P001",
            name="Procurement Test Product",
            category="Testing",
            quantity=10,
            purchase_price=Decimal("100.00"),
            selling_price=Decimal("150.00"),
            reorder_level=5,
            safety_stock=2,
            unit="PCS",
        )

        self.purchase_order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            order_number="PO-TEST-001",
            status="PENDING",
            total_amount=Decimal("500.00"),
        )

        PurchaseOrderItem.objects.create(
            purchase_order=self.purchase_order,
            product=self.product,
            quantity=5,
            unit_price=Decimal("100.00"),
        )

    def test_receiving_purchase_order_increases_stock(self):

        response = self.client.post(
            reverse(
                "receive_purchase",
                args=[self.purchase_order.id],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.product.refresh_from_db()
        self.purchase_order.refresh_from_db()

        self.assertEqual(
            self.product.quantity,
            15,
        )

        self.assertEqual(
            self.purchase_order.status,
            "RECEIVED",
        )

        movement = StockMovement.objects.get(
            product=self.product,
            movement_type="PURCHASE",
        )

        self.assertEqual(
            movement.quantity,
            5,
        )

        self.assertEqual(
            movement.reference,
            "PO-TEST-001",
        )

        self.assertEqual(
            movement.created_by,
            self.user,
        )

    def test_purchase_order_cannot_be_received_twice(self):

        url = reverse(
            "receive_purchase",
            args=[self.purchase_order.id],
        )

        self.client.post(url)

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.quantity,
            15,
        )

        self.client.post(url)

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.quantity,
            15,
        )

        self.assertEqual(
            StockMovement.objects.filter(
                product=self.product,
                movement_type="PURCHASE",
            ).count(),
            1,
        )