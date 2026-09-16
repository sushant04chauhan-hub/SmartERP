from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from procurement.models import PurchaseOrder, Supplier


class DashboardAnalyticsTests(TestCase):

    def setUp(self):

        self.user = get_user_model().objects.create_user(
            username="dashboard_test_user",
            password="test-password-123",
        )

        self.client.force_login(
            self.user
        )

    def test_authenticated_user_can_view_dashboard(self):

        response = self.client.get(
            reverse("dashboard")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_dashboard_contains_analytics_context(self):

        response = self.client.get(
            reverse("dashboard")
        )

        expected_context_keys = [
            "employee_count",
            "department_count",
            "active_employee_count",
            "product_count",
            "low_stock_count",
            "total_revenue",
            "total_paid_expenses",
            "pending_expense_count",
            "completed_sales_count",
            "received_purchase_count",
            "revenue_chart_labels",
            "revenue_chart_data",
            "finance_chart_labels",
            "finance_revenue_data",
            "finance_expense_data",
            "top_product_labels",
            "top_product_data",
            "procurement_chart_labels",
            "procurement_chart_data",
            "top_supplier_labels",
            "top_supplier_data",
            "inventory_value",
            "inventory_status_labels",
            "inventory_status_data",
            "expense_category_labels",
            "expense_category_data",
        ]

        for key in expected_context_keys:
            self.assertIn(
                key,
                response.context,
            )

    def test_dashboard_handles_empty_analytics_data(self):

        response = self.client.get(
            reverse("dashboard")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.context["revenue_chart_labels"],
            [],
        )

        self.assertEqual(
            response.context["revenue_chart_data"],
            [],
        )

        self.assertEqual(
            response.context["procurement_chart_labels"],
            [],
        )

        self.assertEqual(
            response.context["procurement_chart_data"],
            [],
        )

        self.assertEqual(
            response.context["top_product_labels"],
            [],
        )

        self.assertEqual(
            response.context["top_product_data"],
            [],
        )

    def test_received_purchase_without_received_date_does_not_break_dashboard(self):

        supplier = Supplier.objects.create(
            name="Dashboard Test Supplier",
        )

        PurchaseOrder.objects.create(
            supplier=supplier,
            created_by=self.user,
            order_number="PO-DASH-001",
            status="RECEIVED",
            total_amount=Decimal("1000.00"),
            received_date=None,
        )

        response = self.client.get(
            reverse("dashboard")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.context["received_purchase_count"],
            1,
        )

        self.assertEqual(
            response.context["procurement_chart_labels"],
            [],
        )

        self.assertEqual(
            response.context["procurement_chart_data"],
            [],
        )