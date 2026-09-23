from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from audit.models import AuditLog

from finance.models import Expense, Revenue
from finance.services import (
    approve_expense,
    mark_expense_paid,
    reject_expense,
)

from inventory.models import Product, StockMovement
from inventory.services import apply_stock_movement

from procurement.models import (
    PurchaseOrder,
    PurchaseOrderItem,
    Supplier,
)
from procurement.services import (
    approve_purchase_order,
    mark_purchase_order_ordered,
    receive_purchase_order,
)

from sales.models import (
    Customer,
    SalesOrder,
    SalesOrderItem,
)
from sales.services import (
    cancel_sales_order,
    complete_sales_order,
    confirm_sales_order,
)


class WorkflowAuditIntegrationTests(TestCase):

    def setUp(self):

        self.user = (
            get_user_model().objects.create_user(
                username="audit_workflow_user",
                password="test-password-123",
            )
        )

        self.user.profile.role = "MANAGER"
        self.user.profile.save()

        self.product = Product.objects.create(
            product_code="AUD-P001",
            name="Audit Test Product",
            category="Testing",
            quantity=20,
            purchase_price=Decimal("100.00"),
            selling_price=Decimal("150.00"),
            reorder_level=5,
            safety_stock=2,
            unit="PCS",
        )

        self.supplier = Supplier.objects.create(
            name="Audit Test Supplier",
        )

        self.customer = Customer.objects.create(
            name="Audit Test Customer",
        )

    def create_purchase_order(
        self,
        *,
        status="DRAFT",
        quantity=5,
    ):

        purchase_order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            created_by=self.user,
            order_number="AUD-PO-001",
            status=status,
            total_amount=Decimal("500.00"),
        )

        PurchaseOrderItem.objects.create(
            purchase_order=purchase_order,
            product=self.product,
            quantity=quantity,
            unit_price=Decimal("100.00"),
        )

        return purchase_order

    def create_sales_order(
        self,
        *,
        status="DRAFT",
        quantity=4,
    ):

        sales_order = SalesOrder.objects.create(
            customer=self.customer,
            created_by=self.user,
            order_number="AUD-SO-001",
            status=status,
            total_amount=Decimal("600.00"),
        )

        SalesOrderItem.objects.create(
            sales_order=sales_order,
            product=self.product,
            quantity=quantity,
            unit_price=Decimal("150.00"),
        )

        return sales_order

    def create_expense(
        self,
        *,
        status="PENDING",
    ):

        return Expense.objects.create(
            title="Audit Test Expense",
            category="OFFICE",
            amount=Decimal("2000.00"),
            expense_date="2026-09-23",
            reference_number="AUD-EXP-001",
            description="Audit workflow test expense",
            status=status,
            created_by=self.user,
        )

    def test_purchase_approval_creates_audit_log(
        self,
    ):

        purchase_order = (
            self.create_purchase_order()
        )

        approve_purchase_order(
            purchase_order=purchase_order,
            user=self.user,
        )

        log = AuditLog.objects.get(
            action="APPROVE",
            entity_type=(
                "procurement.PurchaseOrder"
            ),
            entity_id=str(
                purchase_order.id
            ),
        )

        self.assertEqual(
            log.actor,
            self.user,
        )

        self.assertEqual(
            log.metadata[
                "previous_status"
            ],
            "DRAFT",
        )

        self.assertEqual(
            log.metadata[
                "new_status"
            ],
            "APPROVED",
        )

    def test_purchase_ordered_creates_audit_log(
        self,
    ):

        purchase_order = (
            self.create_purchase_order(
                status="APPROVED",
            )
        )

        mark_purchase_order_ordered(
            purchase_order=purchase_order,
            user=self.user,
        )

        log = AuditLog.objects.get(
            action="ORDER",
            entity_type=(
                "procurement.PurchaseOrder"
            ),
            entity_id=str(
                purchase_order.id
            ),
        )

        self.assertEqual(
            log.actor,
            self.user,
        )

        self.assertEqual(
            log.metadata[
                "previous_status"
            ],
            "APPROVED",
        )

        self.assertEqual(
            log.metadata[
                "new_status"
            ],
            "ORDERED",
        )

    def test_purchase_receive_creates_related_audit_logs(
        self,
    ):

        purchase_order = (
            self.create_purchase_order(
                status="ORDERED",
                quantity=5,
            )
        )

        receive_purchase_order(
            purchase_order=purchase_order,
            user=self.user,
        )

        self.assertTrue(
            AuditLog.objects.filter(
                action="RECEIVE",
                entity_type=(
                    "procurement.PurchaseOrder"
                ),
                entity_id=str(
                    purchase_order.id
                ),
            ).exists()
        )

        self.assertTrue(
            AuditLog.objects.filter(
                action="STOCK_IN",
                entity_type=(
                    "inventory.StockMovement"
                ),
            ).exists()
        )

        self.assertTrue(
            AuditLog.objects.filter(
                action="CREATE",
                entity_type="finance.Expense",
            ).exists()
        )

        self.assertTrue(
            Expense.objects.filter(
                purchase_order=purchase_order
            ).exists()
        )

    def test_failed_purchase_transition_creates_no_audit_log(
        self,
    ):

        purchase_order = (
            self.create_purchase_order(
                status="DRAFT",
            )
        )

        with self.assertRaises(
            ValidationError
        ):

            receive_purchase_order(
                purchase_order=purchase_order,
                user=self.user,
            )

        self.assertFalse(
            AuditLog.objects.filter(
                entity_type=(
                    "procurement.PurchaseOrder"
                ),
                entity_id=str(
                    purchase_order.id
                ),
            ).exists()
        )

    def test_sales_confirmation_creates_audit_log(
        self,
    ):

        sales_order = (
            self.create_sales_order()
        )

        confirm_sales_order(
            sales_order=sales_order,
            user=self.user,
        )

        log = AuditLog.objects.get(
            action="CONFIRM",
            entity_type="sales.SalesOrder",
            entity_id=str(
                sales_order.id
            ),
        )

        self.assertEqual(
            log.actor,
            self.user,
        )

        self.assertEqual(
            log.metadata[
                "previous_status"
            ],
            "DRAFT",
        )

        self.assertEqual(
            log.metadata[
                "new_status"
            ],
            "CONFIRMED",
        )

    def test_sales_cancellation_creates_audit_log(
        self,
    ):

        sales_order = (
            self.create_sales_order(
                status="CONFIRMED",
            )
        )

        cancel_sales_order(
            sales_order=sales_order,
            user=self.user,
        )

        log = AuditLog.objects.get(
            action="CANCEL",
            entity_type="sales.SalesOrder",
            entity_id=str(
                sales_order.id
            ),
        )

        self.assertEqual(
            log.actor,
            self.user,
        )

        self.assertEqual(
            log.metadata[
                "new_status"
            ],
            "CANCELLED",
        )

    def test_sales_completion_creates_related_audit_logs(
        self,
    ):

        sales_order = (
            self.create_sales_order(
                status="CONFIRMED",
                quantity=4,
            )
        )

        complete_sales_order(
            sales_order=sales_order,
            user=self.user,
        )

        self.assertTrue(
            AuditLog.objects.filter(
                action="COMPLETE",
                entity_type=(
                    "sales.SalesOrder"
                ),
                entity_id=str(
                    sales_order.id
                ),
            ).exists()
        )

        self.assertTrue(
            AuditLog.objects.filter(
                action="STOCK_OUT",
                entity_type=(
                    "inventory.StockMovement"
                ),
            ).exists()
        )

        self.assertTrue(
            AuditLog.objects.filter(
                action="CREATE",
                entity_type="finance.Revenue",
            ).exists()
        )

        self.assertTrue(
            Revenue.objects.filter(
                sales_order=sales_order
            ).exists()
        )

    def test_failed_sales_completion_creates_no_audit_log(
        self,
    ):

        sales_order = (
            self.create_sales_order(
                status="CONFIRMED",
                quantity=100,
            )
        )

        with self.assertRaises(
            ValidationError
        ):

            complete_sales_order(
                sales_order=sales_order,
                user=self.user,
            )

        self.assertFalse(
            AuditLog.objects.filter(
                entity_type="sales.SalesOrder",
                entity_id=str(
                    sales_order.id
                ),
            ).exists()
        )

        self.assertFalse(
            StockMovement.objects.filter(
                reference=(
                    sales_order.order_number
                )
            ).exists()
        )

        self.assertFalse(
            Revenue.objects.filter(
                sales_order=sales_order
            ).exists()
        )

    def test_stock_adjustment_records_stock_before_and_after(
        self,
    ):

        product, movement = (
            apply_stock_movement(
                product=self.product,
                movement_type=(
                    "ADJUSTMENT_IN"
                ),
                quantity=3,
                user=self.user,
                reference="AUD-ADJ-001",
                note="Audit adjustment",
            )
        )

        log = AuditLog.objects.get(
            action="ADJUST",
            entity_type=(
                "inventory.StockMovement"
            ),
            entity_id=str(
                movement.id
            ),
        )

        self.assertEqual(
            log.actor,
            self.user,
        )

        self.assertEqual(
            log.metadata["stock_before"],
            20,
        )

        self.assertEqual(
            log.metadata["stock_after"],
            23,
        )

        self.assertEqual(
            product.quantity,
            23,
        )

    def test_expense_approval_creates_audit_log(
        self,
    ):

        expense = self.create_expense()

        approve_expense(
            expense=expense,
            user=self.user,
        )

        log = AuditLog.objects.get(
            action="APPROVE",
            entity_type="finance.Expense",
            entity_id=str(
                expense.id
            ),
        )

        self.assertEqual(
            log.actor,
            self.user,
        )

        self.assertEqual(
            log.metadata[
                "previous_status"
            ],
            "PENDING",
        )

        self.assertEqual(
            log.metadata[
                "new_status"
            ],
            "APPROVED",
        )

    def test_expense_rejection_creates_audit_log(
        self,
    ):

        expense = self.create_expense()

        reject_expense(
            expense=expense,
            user=self.user,
        )

        log = AuditLog.objects.get(
            action="REJECT",
            entity_type="finance.Expense",
            entity_id=str(
                expense.id
            ),
        )

        self.assertEqual(
            log.actor,
            self.user,
        )

        self.assertEqual(
            log.metadata[
                "new_status"
            ],
            "REJECTED",
        )

    def test_expense_payment_creates_audit_log(
        self,
    ):

        expense = self.create_expense(
            status="APPROVED",
        )

        mark_expense_paid(
            expense=expense,
            user=self.user,
            payment_method="UPI",
        )

        log = AuditLog.objects.get(
            action="PAY",
            entity_type="finance.Expense",
            entity_id=str(
                expense.id
            ),
        )

        self.assertEqual(
            log.actor,
            self.user,
        )

        self.assertEqual(
            log.metadata[
                "previous_status"
            ],
            "APPROVED",
        )

        self.assertEqual(
            log.metadata[
                "new_status"
            ],
            "PAID",
        )

        self.assertEqual(
            log.metadata[
                "payment_method"
            ],
            "UPI",
        )