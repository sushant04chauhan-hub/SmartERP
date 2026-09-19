from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from inventory.models import Product, StockMovement

from .forms import (
    PurchaseOrderForm,
    PurchaseOrderItemFormSet,
)
from .models import (
    PurchaseOrder,
    PurchaseOrderItem,
    Supplier,
)

from .supplier_scoring import (
    calculate_supplier_score,
    get_supplier_performance,
    get_supplier_rating,
    get_supplier_scores,
)

from finance.models import Expense

class ProcurementTests(TestCase):

    def setUp(self):

        User = get_user_model()

        # Procurement user
        self.user = User.objects.create_user(
            username="procurement_test_user",
            password="test-password-123",
        )

        self.user.profile.role = "PROCUREMENT"
        self.user.profile.save()

        # Manager used for approval testing
        self.manager = User.objects.create_user(
            username="manager_test_user",
            password="test-password-123",
        )

        self.manager.profile.role = "MANAGER"
        self.manager.profile.save()

        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            contact_person="Test Contact",
            email="supplier@example.com",
            phone="9999999999",
            is_active=True,
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

        self.second_product = Product.objects.create(
            product_code="PROC-P002",
            name="Second Procurement Product",
            category="Testing",
            quantity=20,
            purchase_price=Decimal("150.00"),
            selling_price=Decimal("220.00"),
            reorder_level=5,
            safety_stock=2,
            unit="PCS",
        )

        self.expected_date = (
            timezone.localdate()
            + timedelta(days=7)
        )

    def create_purchase_order(
        self,
        *,
        order_number="PO-TEST-001",
        status="DRAFT",
    ):

        purchase_order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            created_by=self.user,
            order_number=order_number,
            expected_delivery_date=self.expected_date,
            status=status,
            total_amount=Decimal("500.00"),
        )

        PurchaseOrderItem.objects.create(
            purchase_order=purchase_order,
            product=self.product,
            quantity=5,
            unit_price=Decimal("100.00"),
        )

        return purchase_order

    def get_formset_prefix(self, purchase_order=None):

        if purchase_order is None:
            purchase_order = PurchaseOrder()

        formset = PurchaseOrderItemFormSet(
            instance=purchase_order
        )

        return formset.prefix

    # --------------------------------------------------
    # CREATE PURCHASE ORDER
    # --------------------------------------------------

    def test_create_purchase_order_with_multiple_items(self):

        self.client.force_login(
            self.user
        )

        prefix = self.get_formset_prefix()

        response = self.client.post(
            reverse(
                "purchase_order_create"
            ),
            {
                "order_number": "PO-CREATE-001",
                "supplier": self.supplier.id,
                "expected_delivery_date":
                    self.expected_date.isoformat(),
                "notes": "Automated creation test",

                f"{prefix}-TOTAL_FORMS": "2",
                f"{prefix}-INITIAL_FORMS": "0",
                f"{prefix}-MIN_NUM_FORMS": "1",
                f"{prefix}-MAX_NUM_FORMS": "1000",

                f"{prefix}-0-product":
                    self.product.id,
                f"{prefix}-0-quantity":
                    "2",
                f"{prefix}-0-unit_price":
                    "100.00",

                f"{prefix}-1-product":
                    self.second_product.id,
                f"{prefix}-1-quantity":
                    "2",
                f"{prefix}-1-unit_price":
                    "150.00",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        purchase_order = (
            PurchaseOrder.objects.get(
                order_number="PO-CREATE-001"
            )
        )

        self.assertEqual(
            purchase_order.status,
            "DRAFT",
        )

        self.assertEqual(
            purchase_order.created_by,
            self.user,
        )

        self.assertEqual(
            purchase_order.items.count(),
            2,
        )

        # 2 × 100 + 2 × 150 = 500
        self.assertEqual(
            purchase_order.total_amount,
            Decimal("500.00"),
        )

    # --------------------------------------------------
    # DUPLICATE PRODUCT VALIDATION
    # --------------------------------------------------

    def test_duplicate_product_is_rejected(self):

        self.client.force_login(
            self.user
        )

        prefix = self.get_formset_prefix()

        response = self.client.post(
            reverse(
                "purchase_order_create"
            ),
            {
                "order_number":
                    "PO-DUPLICATE-001",

                "supplier":
                    self.supplier.id,

                "expected_delivery_date":
                    self.expected_date.isoformat(),

                "notes":
                    "Duplicate test",

                f"{prefix}-TOTAL_FORMS": "2",
                f"{prefix}-INITIAL_FORMS": "0",
                f"{prefix}-MIN_NUM_FORMS": "1",
                f"{prefix}-MAX_NUM_FORMS": "1000",

                f"{prefix}-0-product":
                    self.product.id,
                f"{prefix}-0-quantity":
                    "5",
                f"{prefix}-0-unit_price":
                    "100.00",

                f"{prefix}-1-product":
                    self.product.id,
                f"{prefix}-1-quantity":
                    "3",
                f"{prefix}-1-unit_price":
                    "100.00",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertFalse(
            PurchaseOrder.objects.filter(
                order_number=
                    "PO-DUPLICATE-001"
            ).exists()
        )

        self.assertContains(
            response,
            "The same product cannot be added "
            "more than once to a purchase order.",
        )

    # --------------------------------------------------
    # INACTIVE SUPPLIER
    # --------------------------------------------------

    def test_inactive_supplier_not_available_for_new_po(self):

        inactive_supplier = Supplier.objects.create(
            name="Inactive Supplier",
            is_active=False,
        )

        form = PurchaseOrderForm()

        supplier_ids = list(
            form.fields[
                "supplier"
            ].queryset.values_list(
                "id",
                flat=True,
            )
        )

        self.assertIn(
            self.supplier.id,
            supplier_ids,
        )

        self.assertNotIn(
            inactive_supplier.id,
            supplier_ids,
        )

    # --------------------------------------------------
    # EDIT DRAFT PURCHASE ORDER
    # --------------------------------------------------

    def test_draft_purchase_order_can_be_edited(self):

        self.client.force_login(
            self.user
        )

        purchase_order = (
            self.create_purchase_order(
                order_number="PO-EDIT-001",
                status="DRAFT",
            )
        )

        item = purchase_order.items.get()

        prefix = self.get_formset_prefix(
            purchase_order
        )

        response = self.client.post(
            reverse(
                "purchase_order_edit",
                args=[purchase_order.id],
            ),
            {
                "order_number":
                    purchase_order.order_number,

                "supplier":
                    self.supplier.id,

                "expected_delivery_date":
                    self.expected_date.isoformat(),

                "notes":
                    "Edited order",

                f"{prefix}-TOTAL_FORMS": "1",
                f"{prefix}-INITIAL_FORMS": "1",
                f"{prefix}-MIN_NUM_FORMS": "1",
                f"{prefix}-MAX_NUM_FORMS": "1000",

                f"{prefix}-0-id":
                    item.id,

                f"{prefix}-0-product":
                    self.product.id,

                f"{prefix}-0-quantity":
                    "7",

                f"{prefix}-0-unit_price":
                    "100.00",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        purchase_order.refresh_from_db()

        item.refresh_from_db()

        self.assertEqual(
            item.quantity,
            7,
        )

        self.assertEqual(
            purchase_order.total_amount,
            Decimal("700.00"),
        )

    # --------------------------------------------------
    # APPROVED PO CANNOT BE EDITED
    # --------------------------------------------------

    def test_approved_purchase_order_cannot_be_edited(self):

        self.client.force_login(
            self.user
        )

        purchase_order = (
            self.create_purchase_order(
                order_number=
                    "PO-NO-EDIT-001",
                status="APPROVED",
            )
        )

        response = self.client.get(
            reverse(
                "purchase_order_edit",
                args=[purchase_order.id],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        purchase_order.refresh_from_db()

        self.assertEqual(
            purchase_order.status,
            "APPROVED",
        )

    # --------------------------------------------------
    # APPROVAL
    # --------------------------------------------------

    def test_manager_can_approve_purchase_order(self):

        purchase_order = (
            self.create_purchase_order(
                order_number=
                    "PO-APPROVE-001",
                status="DRAFT",
            )
        )

        self.client.force_login(
            self.manager
        )

        response = self.client.post(
            reverse(
                "approve_purchase",
                args=[purchase_order.id],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        purchase_order.refresh_from_db()

        self.assertEqual(
            purchase_order.status,
            "APPROVED",
        )

        self.assertEqual(
            purchase_order.approved_by,
            self.manager,
        )

    # --------------------------------------------------
    # ORDERING
    # --------------------------------------------------

    def test_only_approved_po_can_be_marked_ordered(self):

        purchase_order = (
            self.create_purchase_order(
                order_number=
                    "PO-ORDER-001",
                status="DRAFT",
            )
        )

        self.client.force_login(
            self.user
        )

        # Invalid transition:
        # DRAFT -> ORDERED
        self.client.post(
            reverse(
                "mark_purchase_order",
                args=[purchase_order.id],
            )
        )

        purchase_order.refresh_from_db()

        self.assertEqual(
            purchase_order.status,
            "DRAFT",
        )

        # Valid transition:
        # APPROVED -> ORDERED
        purchase_order.status = "APPROVED"

        purchase_order.save(
            update_fields=["status"]
        )

        self.client.post(
            reverse(
                "mark_purchase_order",
                args=[purchase_order.id],
            )
        )

        purchase_order.refresh_from_db()

        self.assertEqual(
            purchase_order.status,
            "ORDERED",
        )

    # --------------------------------------------------
    # RECEIVING
    # --------------------------------------------------

    def test_receiving_purchase_order_increases_stock(self):

        self.client.force_login(
            self.user
        )

        purchase_order = (
            self.create_purchase_order(
                order_number=
                    "PO-RECEIVE-001",
                status="ORDERED",
            )
        )

        response = self.client.post(
            reverse(
                "receive_purchase",
                args=[purchase_order.id],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.product.refresh_from_db()

        purchase_order.refresh_from_db()

        self.assertEqual(
            self.product.quantity,
            15,
        )

        self.assertEqual(
            purchase_order.status,
            "RECEIVED",
        )

        self.assertEqual(
            purchase_order.received_date,
            timezone.localdate(),
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
            "PO-RECEIVE-001",
        )

        self.assertEqual(
            movement.created_by,
            self.user,
        )
    def test_receiving_purchase_order_creates_finance_expense(self):

        self.client.force_login(
            self.user
        )

        purchase_order = (
            self.create_purchase_order(
                order_number="PO-FIN-001",
                status="ORDERED",
            )
        )

        response = self.client.post(
            reverse(
                "receive_purchase",
                args=[purchase_order.id],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        purchase_order.refresh_from_db()

        self.assertEqual(
            purchase_order.status,
            "RECEIVED",
        )

        expense = Expense.objects.get(
            purchase_order=purchase_order,
        )

        self.assertEqual(
            expense.category,
            "PROCUREMENT",
        )

        self.assertEqual(
            expense.amount,
            purchase_order.total_amount,
        )

        self.assertEqual(
            expense.reference_number,
            purchase_order.order_number,
        )

        self.assertEqual(
            expense.expense_date,
            purchase_order.received_date,
        )

        self.assertEqual(
            expense.status,
            "PENDING",
        )

        self.assertEqual(
            expense.created_by,
            self.user,
        )
    # --------------------------------------------------
    # DUPLICATE RECEIVING
    # --------------------------------------------------

    def test_purchase_order_cannot_be_received_twice(self):

        self.client.force_login(
            self.user
        )

        purchase_order = (
            self.create_purchase_order(
                order_number=
                    "PO-RECEIVE-TWICE-001",
                status="ORDERED",
            )
        )

        url = reverse(
            "receive_purchase",
            args=[purchase_order.id],
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
                        
        self.assertEqual(
            Expense.objects.filter(
                purchase_order=purchase_order,
            ).count(),
            1,
        )

    # --------------------------------------------------
    # CANCELLATION
    # --------------------------------------------------

    def test_ordered_purchase_order_can_be_cancelled(self):

        self.client.force_login(
            self.user
        )

        purchase_order = (
            self.create_purchase_order(
                order_number=
                    "PO-CANCEL-001",
                status="ORDERED",
            )
        )

        response = self.client.post(
            reverse(
                "cancel_purchase",
                args=[purchase_order.id],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        purchase_order.refresh_from_db()

        self.assertEqual(
            purchase_order.status,
            "CANCELLED",
        )

class SupplierScoringTests(TestCase):

    def create_purchase_order(
        self,
        *,
        supplier,
        order_number,
        status,
        expected_date=None,
        received_date=None,
        total_amount="1000.00",
    ):

        return PurchaseOrder.objects.create(
            supplier=supplier,
            order_number=order_number,
            status=status,
            expected_delivery_date=expected_date,
            received_date=received_date,
            total_amount=Decimal(total_amount),
        )

    def test_supplier_performance_metrics_are_calculated(self):

        supplier = Supplier.objects.create(
            name="Performance Test Supplier"
        )

        self.create_purchase_order(
            supplier=supplier,
            order_number="SCORE-PO-001",
            status="RECEIVED",
            expected_date=timezone.datetime(
                2026,
                8,
                10,
            ).date(),
            received_date=timezone.datetime(
                2026,
                8,
                10,
            ).date(),
            total_amount="1000.00",
        )

        self.create_purchase_order(
            supplier=supplier,
            order_number="SCORE-PO-002",
            status="RECEIVED",
            expected_date=timezone.datetime(
                2026,
                8,
                20,
            ).date(),
            received_date=timezone.datetime(
                2026,
                8,
                22,
            ).date(),
            total_amount="2000.00",
        )

        self.create_purchase_order(
            supplier=supplier,
            order_number="SCORE-PO-003",
            status="CANCELLED",
            total_amount="500.00",
        )

        performance = get_supplier_performance()[0]

        self.assertEqual(
            performance["total_orders"],
            3,
        )

        self.assertEqual(
            performance["received_orders"],
            2,
        )

        self.assertEqual(
            performance["cancelled_orders"],
            1,
        )

        self.assertEqual(
            performance["total_received_value"],
            3000.0,
        )

        self.assertEqual(
            performance["delivery_records"],
            2,
        )

        self.assertEqual(
            performance["on_time_deliveries"],
            1,
        )

        self.assertEqual(
            performance["on_time_rate"],
            50.0,
        )

        self.assertEqual(
            performance["average_delay_days"],
            1.0,
        )

        self.assertEqual(
            performance["cancellation_rate"],
            33.33,
        )

    def test_supplier_score_stays_between_zero_and_100(self):

        performance = {
            "total_orders": 5,
            "received_orders": 5,
            "delivery_records": 5,
            "on_time_rate": 80.0,
            "average_delay_days": 1.0,
            "cancellation_rate": 0.0,
        }

        score = calculate_supplier_score(
            performance
        )

        self.assertGreaterEqual(
            score,
            0,
        )

        self.assertLessEqual(
            score,
            100,
        )

    def test_fulfillment_rate_affects_supplier_score(self):

        strong_fulfillment = {
            "total_orders": 5,
            "received_orders": 5,
            "delivery_records": 5,
            "on_time_rate": 80.0,
            "average_delay_days": 1.0,
            "cancellation_rate": 0.0,
        }

        weak_fulfillment = {
            "total_orders": 5,
            "received_orders": 3,
            "delivery_records": 3,
            "on_time_rate": 80.0,
            "average_delay_days": 1.0,
            "cancellation_rate": 0.0,
        }

        strong_score = calculate_supplier_score(
            strong_fulfillment
        )

        weak_score = calculate_supplier_score(
            weak_fulfillment
        )

        self.assertGreater(
            strong_score,
            weak_score,
        )

    def test_cancellation_rate_reduces_supplier_score(self):

        no_cancellations = {
            "total_orders": 5,
            "received_orders": 5,
            "delivery_records": 5,
            "on_time_rate": 80.0,
            "average_delay_days": 1.0,
            "cancellation_rate": 0.0,
        }

        high_cancellations = {
            "total_orders": 5,
            "received_orders": 5,
            "delivery_records": 5,
            "on_time_rate": 80.0,
            "average_delay_days": 1.0,
            "cancellation_rate": 40.0,
        }

        self.assertGreater(
            calculate_supplier_score(
                no_cancellations
            ),
            calculate_supplier_score(
                high_cancellations
            ),
        )

    def test_limited_delivery_history_reduces_confidence(self):

        complete_history = {
            "total_orders": 5,
            "received_orders": 5,
            "delivery_records": 5,
            "on_time_rate": 100.0,
            "average_delay_days": 0.0,
            "cancellation_rate": 0.0,
        }

        limited_history = {
            "total_orders": 5,
            "received_orders": 5,
            "delivery_records": 1,
            "on_time_rate": 100.0,
            "average_delay_days": 0.0,
            "cancellation_rate": 0.0,
        }

        self.assertGreater(
            calculate_supplier_score(
                complete_history
            ),
            calculate_supplier_score(
                limited_history
            ),
        )

    def test_supplier_rating_thresholds(self):

        self.assertEqual(
            get_supplier_rating(85),
            "EXCELLENT",
        )

        self.assertEqual(
            get_supplier_rating(70),
            "GOOD",
        )

        self.assertEqual(
            get_supplier_rating(55),
            "FAIR",
        )

        self.assertEqual(
            get_supplier_rating(54.99),
            "NEEDS_REVIEW",
        )

    def test_supplier_scores_are_sorted_highest_first(self):

        reliable_supplier = Supplier.objects.create(
            name="Reliable Supplier"
        )

        delayed_supplier = Supplier.objects.create(
            name="Delayed Supplier"
        )

        for index in range(5):

            expected_date = timezone.datetime(
                2026,
                7,
                1 + index,
            ).date()

            self.create_purchase_order(
                supplier=reliable_supplier,
                order_number=(
                    f"RELIABLE-{index}"
                ),
                status="RECEIVED",
                expected_date=expected_date,
                received_date=expected_date,
            )

            self.create_purchase_order(
                supplier=delayed_supplier,
                order_number=(
                    f"DELAYED-{index}"
                ),
                status="RECEIVED",
                expected_date=expected_date,
                received_date=(
                    expected_date
                    + timedelta(days=5)
                ),
            )

        scores = get_supplier_scores()

        self.assertEqual(
            scores[0]["supplier_name"],
            "Reliable Supplier",
        )

        self.assertGreater(
            scores[0]["supplier_score"],
            scores[1]["supplier_score"],
        )