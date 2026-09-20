from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class DashboardApiTests(TestCase):

    def setUp(self):

        self.user = (
            get_user_model().objects.create_user(
                username="dashboard_api_user",
                password="test-password-123",
            )
        )

    def test_dashboard_api_requires_authentication(
        self,
    ):

        response = self.client.get(
            reverse("api_dashboard")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_authenticated_user_can_view_dashboard(
        self,
    ):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("api_dashboard")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_dashboard_contains_core_kpis(
        self,
    ):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("api_dashboard")
        )

        data = response.json()

        expected_fields = {
            "employee_count",
            "department_count",
            "active_employee_count",
            "product_count",
            "low_stock_count",
            "inventory_value",
            "total_revenue",
            "total_paid_expenses",
            "pending_expense_count",
            "completed_sales_count",
            "received_purchase_count",
        }

        self.assertTrue(
            expected_fields.issubset(
                data.keys()
            )
        )

    def test_dashboard_contains_analytics_data(
        self,
    ):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("api_dashboard")
        )

        data = response.json()

        expected_fields = {
            "revenue_chart_labels",
            "revenue_chart_data",
            "finance_chart_labels",
            "finance_revenue_data",
            "finance_expense_data",
            "top_product_labels",
            "top_product_data",
            "inventory_status_labels",
            "inventory_status_data",
            "forecast_chart_labels",
            "forecast_chart_data",
            "supplier_score_labels",
            "supplier_score_data",
        }

        self.assertTrue(
            expected_fields.issubset(
                data.keys()
            )
        )

    def test_dashboard_api_is_read_only(
        self,
    ):

        self.client.force_login(
            self.user
        )

        response = self.client.post(
            reverse("api_dashboard"),
            {},
        )

        self.assertEqual(
            response.status_code,
            405,
        )