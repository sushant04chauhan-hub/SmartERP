from decimal import Decimal

from django.contrib.auth import (
    get_user_model,
)
from django.test import TestCase

from notifications.models import (
    Notification,
)

from .models import Product
from .tasks import (
    build_inventory_health_snapshot,
    monitor_low_stock_products,
)


class InventoryBackgroundTaskTests(
    TestCase
):

    def create_product(
        self,
        *,
        code,
        quantity,
        reorder_level,
        safety_stock,
    ):
        return Product.objects.create(
            product_code=code,
            name=f"Product {code}",
            category="Task Test",
            quantity=quantity,
            purchase_price=Decimal(
                "100.00"
            ),
            selling_price=Decimal(
                "150.00"
            ),
            reorder_level=reorder_level,
            safety_stock=safety_stock,
            unit="PCS",
        )

    def create_user(
        self,
        *,
        username,
        role,
    ):
        User = get_user_model()

        user = User.objects.create_user(
            username=username,
            password=(
                "test-password-123"
            ),
        )

        user.profile.role = role
        user.profile.save()

        return user

    def test_inventory_health_snapshot(
        self,
    ):
        self.create_product(
            code="TASK-001",
            quantity=20,
            reorder_level=5,
            safety_stock=2,
        )

        self.create_product(
            code="TASK-002",
            quantity=5,
            reorder_level=5,
            safety_stock=2,
        )

        self.create_product(
            code="TASK-003",
            quantity=1,
            reorder_level=5,
            safety_stock=2,
        )

        self.create_product(
            code="TASK-004",
            quantity=0,
            reorder_level=5,
            safety_stock=2,
        )

        result = (
            build_inventory_health_snapshot
            .apply()
            .get()
        )

        self.assertEqual(
            result["total_products"],
            4,
        )

        self.assertEqual(
            result[
                "low_stock_products"
            ],
            3,
        )

        self.assertEqual(
            result[
                "below_safety_stock_products"
            ],
            2,
        )

        self.assertEqual(
            result[
                "out_of_stock_products"
            ],
            1,
        )

    def test_low_stock_monitor_notifies_correct_roles(
        self,
    ):
        inventory_user = (
            self.create_user(
                username=(
                    "task_inventory"
                ),
                role="INVENTORY",
            )
        )

        manager_user = (
            self.create_user(
                username=(
                    "task_manager"
                ),
                role="MANAGER",
            )
        )

        finance_user = (
            self.create_user(
                username=(
                    "task_finance"
                ),
                role="FINANCE",
            )
        )

        product = self.create_product(
            code="TASK-LOW",
            quantity=3,
            reorder_level=5,
            safety_stock=2,
        )

        result = (
            monitor_low_stock_products
            .apply()
            .get()
        )

        self.assertEqual(
            result[
                "notifications_created"
            ],
            2,
        )

        self.assertTrue(
            Notification.objects.filter(
                recipient=inventory_user,
                entity_id=str(
                    product.id
                ),
            ).exists()
        )

        self.assertTrue(
            Notification.objects.filter(
                recipient=manager_user,
                entity_id=str(
                    product.id
                ),
            ).exists()
        )

        self.assertFalse(
            Notification.objects.filter(
                recipient=finance_user,
                entity_id=str(
                    product.id
                ),
            ).exists()
        )

    def test_low_stock_monitor_uses_cooldown(
        self,
    ):
        self.create_user(
            username=(
                "task_inventory_cooldown"
            ),
            role="INVENTORY",
        )

        self.create_product(
            code="TASK-COOLDOWN",
            quantity=2,
            reorder_level=5,
            safety_stock=2,
        )

        first_result = (
            monitor_low_stock_products
            .apply()
            .get()
        )

        second_result = (
            monitor_low_stock_products
            .apply()
            .get()
        )

        self.assertEqual(
            first_result[
                "notifications_created"
            ],
            1,
        )

        self.assertEqual(
            second_result[
                "notifications_created"
            ],
            0,
        )

        self.assertEqual(
            second_result[
                "notifications_skipped"
            ],
            1,
        )

    def test_out_of_stock_alert_is_critical(
        self,
    ):
        user = self.create_user(
            username=(
                "task_inventory_critical"
            ),
            role="INVENTORY",
        )

        product = self.create_product(
            code="TASK-ZERO",
            quantity=0,
            reorder_level=5,
            safety_stock=2,
        )

        (
            monitor_low_stock_products
            .apply()
            .get()
        )

        notification = (
            Notification.objects.get(
                recipient=user,
                entity_id=str(
                    product.id
                ),
            )
        )

        self.assertEqual(
            notification.priority,
            "CRITICAL",
        )

        self.assertEqual(
            notification.notification_type,
            "ACTION_REQUIRED",
        )