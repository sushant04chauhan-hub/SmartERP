from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from inventory.models import Product, StockMovement

from .forms import (
    SalesOrderForm,
    SalesOrderItemFormSet,
)
from .models import (
    Customer,
    SalesOrder,
    SalesOrderItem,
)


class SalesTests(TestCase):

    def setUp(self):

        User = get_user_model()

        self.user = User.objects.create_user(
            username="sales_test_user",
            password="test-password-123",
        )

        self.user.profile.role = "SALES"
        self.user.profile.save()

        self.client.force_login(
            self.user
        )

        self.customer = Customer.objects.create(
            name="Test Customer",
            email="customer@example.com",
            phone="9876543210",
            address="Test Address",
            is_active=True,
        )

        self.product = Product.objects.create(
            product_code="SALE-P001",
            name="Sales Test Product",
            category="Testing",
            quantity=10,
            purchase_price=Decimal("100.00"),
            selling_price=Decimal("150.00"),
            reorder_level=3,
            safety_stock=2,
            unit="PCS",
        )

        self.second_product = Product.objects.create(
            product_code="SALE-P002",
            name="Second Sales Product",
            category="Testing",
            quantity=5,
            purchase_price=Decimal("200.00"),
            selling_price=Decimal("300.00"),
            reorder_level=2,
            safety_stock=1,
            unit="PCS",
        )

    def create_sales_order(
        self,
        *,
        order_number="SO-TEST-001",
        status="DRAFT",
        product=None,
        quantity=2,
        unit_price=None,
    ):

        if product is None:
            product = self.product

        if unit_price is None:
            unit_price = product.selling_price

        sales_order = SalesOrder.objects.create(
            customer=self.customer,
            created_by=self.user,
            order_number=order_number,
            status=status,
            total_amount=(
                Decimal(str(quantity))
                * unit_price
            ),
        )

        SalesOrderItem.objects.create(
            sales_order=sales_order,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
        )

        return sales_order

    def get_formset_prefix(
        self,
        sales_order=None,
    ):

        if sales_order is None:
            sales_order = SalesOrder()

        formset = SalesOrderItemFormSet(
            instance=sales_order
        )

        return formset.prefix

    # --------------------------------------------------
    # CREATE SALES ORDER
    # --------------------------------------------------

    def test_create_sales_order_with_multiple_items(self):

        prefix = self.get_formset_prefix()

        response = self.client.post(
            reverse(
                "sales_order_create"
            ),
            {
                "order_number": "SO-CREATE-001",
                "customer": self.customer.id,
                "notes": "Sales creation test",

                f"{prefix}-TOTAL_FORMS": "2",
                f"{prefix}-INITIAL_FORMS": "0",
                f"{prefix}-MIN_NUM_FORMS": "1",
                f"{prefix}-MAX_NUM_FORMS": "1000",

                f"{prefix}-0-product":
                    self.product.id,

                f"{prefix}-0-quantity":
                    "2",

                f"{prefix}-0-unit_price":
                    "150.00",

                f"{prefix}-1-product":
                    self.second_product.id,

                f"{prefix}-1-quantity":
                    "3",

                f"{prefix}-1-unit_price":
                    "300.00",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        sales_order = SalesOrder.objects.get(
            order_number="SO-CREATE-001"
        )

        self.assertEqual(
            sales_order.status,
            "DRAFT",
        )

        self.assertEqual(
            sales_order.created_by,
            self.user,
        )

        self.assertEqual(
            sales_order.items.count(),
            2,
        )

        # 2 × 150 + 3 × 300 = 1200
        self.assertEqual(
            sales_order.total_amount,
            Decimal("1200.00"),
        )

        # Creating a draft must not change inventory.
        self.product.refresh_from_db()
        self.second_product.refresh_from_db()

        self.assertEqual(
            self.product.quantity,
            10,
        )

        self.assertEqual(
            self.second_product.quantity,
            5,
        )

    # --------------------------------------------------
    # DUPLICATE PRODUCT VALIDATION
    # --------------------------------------------------

    def test_duplicate_product_is_rejected(self):

        prefix = self.get_formset_prefix()

        response = self.client.post(
            reverse(
                "sales_order_create"
            ),
            {
                "order_number":
                    "SO-DUPLICATE-001",

                "customer":
                    self.customer.id,

                "notes":
                    "Duplicate product test",

                f"{prefix}-TOTAL_FORMS": "2",
                f"{prefix}-INITIAL_FORMS": "0",
                f"{prefix}-MIN_NUM_FORMS": "1",
                f"{prefix}-MAX_NUM_FORMS": "1000",

                f"{prefix}-0-product":
                    self.product.id,

                f"{prefix}-0-quantity":
                    "2",

                f"{prefix}-0-unit_price":
                    "150.00",

                f"{prefix}-1-product":
                    self.product.id,

                f"{prefix}-1-quantity":
                    "1",

                f"{prefix}-1-unit_price":
                    "150.00",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertFalse(
            SalesOrder.objects.filter(
                order_number=
                    "SO-DUPLICATE-001"
            ).exists()
        )

        self.assertContains(
            response,
            "The same product cannot be added "
            "more than once to a sales order.",
        )

    # --------------------------------------------------
    # INACTIVE CUSTOMER
    # --------------------------------------------------

    def test_inactive_customer_not_available_for_new_order(self):

        inactive_customer = (
            Customer.objects.create(
                name="Inactive Customer",
                is_active=False,
            )
        )

        form = SalesOrderForm()

        customer_ids = list(
            form.fields[
                "customer"
            ].queryset.values_list(
                "id",
                flat=True,
            )
        )

        self.assertIn(
            self.customer.id,
            customer_ids,
        )

        self.assertNotIn(
            inactive_customer.id,
            customer_ids,
        )

    # --------------------------------------------------
    # EDIT DRAFT SALES ORDER
    # --------------------------------------------------

    def test_draft_sales_order_can_be_edited(self):

        sales_order = self.create_sales_order(
            order_number="SO-EDIT-001",
            status="DRAFT",
        )

        item = sales_order.items.get()

        prefix = self.get_formset_prefix(
            sales_order
        )

        response = self.client.post(
            reverse(
                "sales_order_edit",
                args=[sales_order.id],
            ),
            {
                "order_number":
                    sales_order.order_number,

                "customer":
                    self.customer.id,

                "notes":
                    "Edited sales order",

                f"{prefix}-TOTAL_FORMS": "1",
                f"{prefix}-INITIAL_FORMS": "1",
                f"{prefix}-MIN_NUM_FORMS": "1",
                f"{prefix}-MAX_NUM_FORMS": "1000",

                f"{prefix}-0-id":
                    item.id,

                f"{prefix}-0-product":
                    self.product.id,

                f"{prefix}-0-quantity":
                    "4",

                f"{prefix}-0-unit_price":
                    "140.00",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        sales_order.refresh_from_db()
        item.refresh_from_db()

        self.assertEqual(
            item.quantity,
            4,
        )

        self.assertEqual(
            item.unit_price,
            Decimal("140.00"),
        )

        self.assertEqual(
            sales_order.total_amount,
            Decimal("560.00"),
        )

        # Editing a draft must not affect inventory.
        self.product.refresh_from_db()

        self.assertEqual(
            self.product.quantity,
            10,
        )

    # --------------------------------------------------
    # NON-DRAFT ORDER CANNOT BE EDITED
    # --------------------------------------------------

    def test_confirmed_sales_order_cannot_be_edited(self):

        sales_order = self.create_sales_order(
            order_number="SO-NO-EDIT-001",
            status="CONFIRMED",
        )

        response = self.client.get(
            reverse(
                "sales_order_edit",
                args=[sales_order.id],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        sales_order.refresh_from_db()

        self.assertEqual(
            sales_order.status,
            "CONFIRMED",
        )

    # --------------------------------------------------
    # CONFIRM SALES ORDER
    # --------------------------------------------------

    def test_draft_sales_order_can_be_confirmed(self):

        sales_order = self.create_sales_order(
            order_number="SO-CONFIRM-001",
            status="DRAFT",
        )

        response = self.client.post(
            reverse(
                "confirm_order",
                args=[sales_order.id],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        sales_order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            sales_order.status,
            "CONFIRMED",
        )

        # Confirming alone must not reduce stock.
        self.assertEqual(
            self.product.quantity,
            10,
        )

        self.assertEqual(
            StockMovement.objects.filter(
                movement_type="SALE"
            ).count(),
            0,
        )

    # --------------------------------------------------
    # CANCEL SALES ORDER
    # --------------------------------------------------

    def test_confirmed_sales_order_can_be_cancelled(self):

        sales_order = self.create_sales_order(
            order_number="SO-CANCEL-001",
            status="CONFIRMED",
        )

        response = self.client.post(
            reverse(
                "cancel_order",
                args=[sales_order.id],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        sales_order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            sales_order.status,
            "CANCELLED",
        )

        self.assertEqual(
            self.product.quantity,
            10,
        )

        self.assertFalse(
            StockMovement.objects.filter(
                movement_type="SALE",
                reference="SO-CANCEL-001",
            ).exists()
        )

    # --------------------------------------------------
    # COMPLETE SALES ORDER
    # --------------------------------------------------

    def test_completing_sales_order_decreases_stock(self):

        sales_order = self.create_sales_order(
            order_number="SO-COMPLETE-001",
            status="CONFIRMED",
            quantity=3,
        )

        response = self.client.post(
            reverse(
                "complete_order",
                args=[sales_order.id],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        sales_order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            sales_order.status,
            "COMPLETED",
        )

        self.assertEqual(
            sales_order.completed_date,
            timezone.localdate(),
        )

        self.assertEqual(
            self.product.quantity,
            7,
        )

        movement = StockMovement.objects.get(
            product=self.product,
            movement_type="SALE",
            reference="SO-COMPLETE-001",
        )

        self.assertEqual(
            movement.quantity,
            3,
        )

        self.assertEqual(
            movement.created_by,
            self.user,
        )

        self.assertEqual(
            movement.note,
            "Stock issued for sales order",
        )

    # --------------------------------------------------
    # INSUFFICIENT STOCK
    # --------------------------------------------------

    def test_insufficient_stock_blocks_completion(self):

        sales_order = self.create_sales_order(
            order_number=
                "SO-NO-STOCK-001",
            status="CONFIRMED",
            quantity=20,
        )

        response = self.client.post(
            reverse(
                "complete_order",
                args=[sales_order.id],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        sales_order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            sales_order.status,
            "CONFIRMED",
        )

        self.assertIsNone(
            sales_order.completed_date,
        )

        self.assertEqual(
            self.product.quantity,
            10,
        )

        self.assertFalse(
            StockMovement.objects.filter(
                movement_type="SALE",
                reference="SO-NO-STOCK-001",
            ).exists()
        )

    # --------------------------------------------------
    # ATOMIC MULTI-ITEM COMPLETION
    # --------------------------------------------------

    def test_multi_item_sale_is_atomic_if_stock_is_insufficient(self):

        sales_order = SalesOrder.objects.create(
            customer=self.customer,
            created_by=self.user,
            order_number=
                "SO-ATOMIC-001",
            status="CONFIRMED",
            total_amount=
                Decimal("1800.00"),
        )

        SalesOrderItem.objects.create(
            sales_order=sales_order,
            product=self.product,
            quantity=2,
            unit_price=Decimal("150.00"),
        )

        SalesOrderItem.objects.create(
            sales_order=sales_order,
            product=self.second_product,
            quantity=6,
            unit_price=Decimal("250.00"),
        )

        # Product 1 has enough:
        # 10 available, 2 required.
        #
        # Product 2 does NOT:
        # 5 available, 6 required.

        response = self.client.post(
            reverse(
                "complete_order",
                args=[sales_order.id],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        sales_order.refresh_from_db()
        self.product.refresh_from_db()
        self.second_product.refresh_from_db()

        self.assertEqual(
            sales_order.status,
            "CONFIRMED",
        )

        self.assertEqual(
            self.product.quantity,
            10,
        )

        self.assertEqual(
            self.second_product.quantity,
            5,
        )

        self.assertEqual(
            StockMovement.objects.filter(
                movement_type="SALE",
                reference="SO-ATOMIC-001",
            ).count(),
            0,
        )

    # --------------------------------------------------
    # DOUBLE COMPLETION
    # --------------------------------------------------

    def test_sales_order_cannot_be_completed_twice(self):

        sales_order = self.create_sales_order(
            order_number=
                "SO-TWICE-001",
            status="CONFIRMED",
            quantity=2,
        )

        url = reverse(
            "complete_order",
            args=[sales_order.id],
        )

        self.client.post(url)

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.quantity,
            8,
        )

        self.client.post(url)

        self.product.refresh_from_db()
        sales_order.refresh_from_db()

        self.assertEqual(
            self.product.quantity,
            8,
        )

        self.assertEqual(
            sales_order.status,
            "COMPLETED",
        )

        self.assertEqual(
            StockMovement.objects.filter(
                product=self.product,
                movement_type="SALE",
                reference="SO-TWICE-001",
            ).count(),
            1,
        )

    # --------------------------------------------------
    # INVALID CONFIRM TRANSITION
    # --------------------------------------------------

    def test_confirmed_order_cannot_be_confirmed_again(self):

        sales_order = self.create_sales_order(
            order_number=
                "SO-CONFIRM-TWICE-001",
            status="CONFIRMED",
        )

        response = self.client.post(
            reverse(
                "confirm_order",
                args=[sales_order.id],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        sales_order.refresh_from_db()

        self.assertEqual(
            sales_order.status,
            "CONFIRMED",
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.quantity,
            10,
        )

    # --------------------------------------------------
    # COMPLETED ORDER CANNOT BE CANCELLED
    # --------------------------------------------------

    def test_completed_sales_order_cannot_be_cancelled(self):

        sales_order = self.create_sales_order(
            order_number=
                "SO-COMPLETE-CANCEL-001",
            status="CONFIRMED",
            quantity=2,
        )

        self.client.post(
            reverse(
                "complete_order",
                args=[sales_order.id],
            )
        )

        self.client.post(
            reverse(
                "cancel_order",
                args=[sales_order.id],
            )
        )

        sales_order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            sales_order.status,
            "COMPLETED",
        )

        self.assertEqual(
            self.product.quantity,
            8,
        )