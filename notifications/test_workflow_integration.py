from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from finance.models import Expense
from finance.services import (
    approve_expense,
    reject_expense,
)

from inventory.models import Product
from inventory.services import apply_stock_movement

from notifications.models import Notification

from procurement.models import (
    PurchaseOrder,
    PurchaseOrderItem,
    Supplier,
)
from procurement.services import (
    approve_purchase_order,
    receive_purchase_order,
)

from sales.models import (
    Customer,
    SalesOrder,
    SalesOrderItem,
)
from sales.services import (
    complete_sales_order,
)


class NotificationWorkflowIntegrationTests(
    TestCase
):

    def setUp(self):

        User = get_user_model()

        self.manager = User.objects.create_user(
            username="notification_manager",
            password="test-password-123",
        )

        self.manager.profile.role = "MANAGER"
        self.manager.profile.save()

        self.procurement_user = (
            User.objects.create_user(
                username="notification_procurement",
                password="test-password-123",
            )
        )

        self.procurement_user.profile.role = (
            "PROCUREMENT"
        )
        self.procurement_user.profile.save()

        self.finance_user = (
            User.objects.create_user(
                username="notification_finance",
                password="test-password-123",
            )
        )

        self.finance_user.profile.role = (
            "FINANCE"
        )
        self.finance_user.profile.save()

        self.inventory_user = (
            User.objects.create_user(
                username="notification_inventory",
                password="test-password-123",
            )
        )

        self.inventory_user.profile.role = (
            "INVENTORY"
        )
        self.inventory_user.profile.save()

        self.sales_user = (
            User.objects.create_user(
                username="notification_sales",
                password="test-password-123",
            )
        )

        self.sales_user.profile.role = (
            "SALES"
        )
        self.sales_user.profile.save()

        self.product = Product.objects.create(
            product_code="NOT-P001",
            name="Notification Product",
            category="Testing",
            quantity=20,
            purchase_price=Decimal("100.00"),
            selling_price=Decimal("150.00"),
            reorder_level=5,
            safety_stock=2,
            unit="PCS",
        )

        self.supplier = Supplier.objects.create(
            name="Notification Supplier",
        )

        self.customer = Customer.objects.create(
            name="Notification Customer",
        )

    def test_purchase_approval_notifies_procurement_users(
        self,
    ):

        purchase_order = (
            PurchaseOrder.objects.create(
                supplier=self.supplier,
                created_by=self.manager,
                order_number="NOT-PO-001",
                total_amount=Decimal(
                    "500.00"
                ),
            )
        )

        approve_purchase_order(
            purchase_order=purchase_order,
            user=self.manager,
        )

        notification = (
            Notification.objects.get(
                recipient=(
                    self.procurement_user
                ),
                title=(
                    "Purchase order approved"
                ),
            )
        )

        self.assertEqual(
            notification.target_url,
            "/procurement",
        )

    def test_received_purchase_creates_finance_notification(
        self,
    ):

        purchase_order = (
            PurchaseOrder.objects.create(
                supplier=self.supplier,
                created_by=(
                    self.procurement_user
                ),
                order_number="NOT-PO-002",
                status="ORDERED",
                total_amount=Decimal(
                    "500.00"
                ),
            )
        )

        PurchaseOrderItem.objects.create(
            purchase_order=purchase_order,
            product=self.product,
            quantity=5,
            unit_price=Decimal("100.00"),
        )

        receive_purchase_order(
            purchase_order=purchase_order,
            user=self.procurement_user,
        )

        notification = (
            Notification.objects.get(
                recipient=self.finance_user,
                title=(
                    "Expense requires review"
                ),
            )
        )

        self.assertEqual(
            notification.priority,
            "HIGH",
        )

        self.assertEqual(
            notification.notification_type,
            "ACTION_REQUIRED",
        )

    def test_completed_sale_creates_finance_notification(
        self,
    ):

        sales_order = SalesOrder.objects.create(
            customer=self.customer,
            created_by=self.sales_user,
            order_number="NOT-SO-001",
            status="CONFIRMED",
            total_amount=Decimal("300.00"),
        )

        SalesOrderItem.objects.create(
            sales_order=sales_order,
            product=self.product,
            quantity=2,
            unit_price=Decimal("150.00"),
        )

        complete_sales_order(
            sales_order=sales_order,
            user=self.sales_user,
        )

        self.assertTrue(
            Notification.objects.filter(
                recipient=self.finance_user,
                title=(
                    "Sales revenue recorded"
                ),
            ).exists()
        )

    def test_low_stock_threshold_creates_inventory_notification(
        self,
    ):

        apply_stock_movement(
            product=self.product,
            movement_type="SALE",
            quantity=15,
            user=self.sales_user,
            reference="NOT-STOCK-001",
        )

        notification = (
            Notification.objects.get(
                recipient=self.inventory_user,
                title="Low stock alert",
            )
        )

        self.assertEqual(
            notification.priority,
            "HIGH",
        )

    def test_low_stock_does_not_repeat_while_already_low(
        self,
    ):

        self.product.quantity = 6
        self.product.save()

        apply_stock_movement(
            product=self.product,
            movement_type="SALE",
            quantity=1,
            user=self.sales_user,
        )

        first_count = (
            Notification.objects.filter(
                recipient=self.inventory_user,
                title="Low stock alert",
            ).count()
        )

        self.product.refresh_from_db()

        apply_stock_movement(
            product=self.product,
            movement_type="SALE",
            quantity=1,
            user=self.sales_user,
        )

        second_count = (
            Notification.objects.filter(
                recipient=self.inventory_user,
                title="Low stock alert",
            ).count()
        )

        self.assertEqual(
            first_count,
            1,
        )

        self.assertEqual(
            second_count,
            1,
        )

    def test_expense_approval_notifies_creator(
        self,
    ):

        expense = Expense.objects.create(
            title="Creator Expense",
            category="OFFICE",
            amount=Decimal("1000.00"),
            expense_date="2026-09-23",
            created_by=self.procurement_user,
        )

        approve_expense(
            expense=expense,
            user=self.finance_user,
        )

        self.assertTrue(
            Notification.objects.filter(
                recipient=(
                    self.procurement_user
                ),
                title="Expense approved",
            ).exists()
        )

    def test_expense_rejection_notifies_creator(
        self,
    ):

        expense = Expense.objects.create(
            title="Rejected Expense",
            category="OFFICE",
            amount=Decimal("1000.00"),
            expense_date="2026-09-23",
            created_by=self.procurement_user,
        )

        reject_expense(
            expense=expense,
            user=self.finance_user,
        )

        notification = (
            Notification.objects.get(
                recipient=(
                    self.procurement_user
                ),
                title="Expense rejected",
            )
        )

        self.assertEqual(
            notification.priority,
            "HIGH",
        )

    def test_actor_does_not_receive_own_role_notification(
        self,
    ):

        purchase_order = (
            PurchaseOrder.objects.create(
                supplier=self.supplier,
                created_by=(
                    self.procurement_user
                ),
                order_number="NOT-PO-003",
                total_amount=Decimal(
                    "500.00"
                ),
            )
        )

        approve_purchase_order(
            purchase_order=purchase_order,
            user=self.procurement_user,
        )

        self.assertFalse(
            Notification.objects.filter(
                recipient=(
                    self.procurement_user
                ),
                title=(
                    "Purchase order approved"
                ),
            ).exists()
        )