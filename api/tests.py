from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from decimal import Decimal
from datetime import date
from finance.models import Expense, Revenue
from hr.models import Department, Employee

from inventory.models import Product
from procurement.models import (
    PurchaseOrder,
    PurchaseOrderItem,
    Supplier,
)

from sales.models import (
    Customer,
    SalesOrder,
    SalesOrderItem,
)

class ProductApiTests(TestCase):

    def setUp(self):

        self.user = get_user_model().objects.create_user(
            username="api_test_user",
            password="test-password-123",
        )

        self.product = Product.objects.create(
            product_code="API001",
            name="API Test Product",
            category="Electronics",
            description="Product used for API testing",
            quantity=10,
            purchase_price=1000,
            selling_price=1500,
            reorder_level=5,
            safety_stock=2,
            unit="PCS",
        )

    def test_product_list_requires_authentication(self):

        response = self.client.get(
            reverse("api_product_list")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_authenticated_user_can_view_product_list(self):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("api_product_list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["count"],
            1,
        )

        self.assertEqual(
            len(data["results"]),
            1,
        )

        self.assertEqual(
            data["results"][0]["product_code"],
            "API001",
        )

    def test_authenticated_user_can_view_product_detail(self):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse(
                "api_product_detail",
                args=[self.product.id],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json()["name"],
            "API Test Product",
        )

    def test_product_list_can_search_by_name(self):

        Product.objects.create(
            product_code="API002",
            name="Laptop Stand",
            category="Accessories",
            description="Adjustable laptop stand",
            quantity=5,
            purchase_price=500,
            selling_price=800,
            reorder_level=2,
            safety_stock=1,
            unit="PCS",
        )

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("api_product_list"),
            {
                "search": "Laptop",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["count"],
            1,
        )

        self.assertEqual(
            len(data["results"]),
            1,
        )

        self.assertEqual(
            data["results"][0]["product_code"],
            "API002",
        )


    def test_product_list_can_order_by_quantity_descending(self):

        Product.objects.create(
            product_code="API003",
            name="High Stock Product",
            category="Electronics",
            description="High quantity product",
            quantity=50,
            purchase_price=200,
            selling_price=300,
            reorder_level=5,
            safety_stock=2,
            unit="PCS",
        )

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("api_product_list"),
            {
                "ordering": "-quantity",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()
        
        self.assertEqual(
            data["results"][0]["product_code"],
            "API003",
        )

    def test_product_list_pagination_with_page_size(self):

        for index in range(1, 16):

            Product.objects.create(
                product_code=f"PAGE{index:03d}",
                name=f"Pagination Product {index}",
                category="Electronics",
                description="Pagination test product",
                quantity=index,
                purchase_price=100,
                selling_price=150,
                reorder_level=2,
                safety_stock=1,
                unit="PCS",
            )

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("api_product_list"),
            {
                "page_size": 5,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["count"],
            16,
        )

        self.assertEqual(
            len(data["results"]),
            5,
        )

        self.assertIsNotNone(
            data["next"]
        )

        self.assertIsNone(
            data["previous"]
        )

    def test_product_list_does_not_allow_post(self):
    
        self.client.force_login(
            self.user
        )
    
        response = self.client.post(
            reverse("api_product_list"),
            {
                "product_code": "API999",
                "name": "Blocked Product",
                "category": "Electronics",
                "quantity": 10,
            },
        )
    
        self.assertEqual(
            response.status_code,
            405,
        )
    
        self.assertFalse(
            Product.objects.filter(
                product_code="API999"
            ).exists()
        )

class PurchaseOrderApiTests(TestCase):

    def setUp(self):

        self.user = get_user_model().objects.create_user(
            username="procurement_api_user",
            password="test-password-123",
        )

        self.supplier = Supplier.objects.create(
            name="API Test Supplier",
            contact_person="Test Contact",
            email="supplier@example.com",
        )

        self.product = Product.objects.create(
            product_code="POAPI001",
            name="Procurement API Product",
            category="Electronics",
            description="Product for purchase order API test",
            quantity=20,
            purchase_price=Decimal("500.00"),
            selling_price=Decimal("750.00"),
            reorder_level=5,
            safety_stock=2,
            unit="PCS",
        )

        self.purchase_order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            created_by=self.user,
            order_number="PO-API-001",
            status="ORDERED",
            total_amount=Decimal("1500.00"),
            notes="API test purchase order",
        )

        PurchaseOrderItem.objects.create(
            purchase_order=self.purchase_order,
            product=self.product,
            quantity=3,
            unit_price=Decimal("500.00"),
        )

    def test_purchase_order_list_requires_authentication(self):

        response = self.client.get(
            reverse("api_purchase_order_list")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_authenticated_user_can_view_purchase_order_list(self):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("api_purchase_order_list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["count"],
            1,
        )

        self.assertEqual(
            len(data["results"]),
            1,
        )

        self.assertEqual(
            data["results"][0]["order_number"],
            "PO-API-001",
        )

        self.assertEqual(
            data["results"][0]["supplier_name"],
            "API Test Supplier",
        )

    def test_purchase_order_detail_includes_items(self):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse(
                "api_purchase_order_detail",
                args=[self.purchase_order.id],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["order_number"],
            "PO-API-001",
        )

        self.assertEqual(
            len(data["items"]),
            1,
        )

        self.assertEqual(
            data["items"][0]["product_code"],
            "POAPI001",
        )

        self.assertEqual(
            data["items"][0]["product_name"],
            "Procurement API Product",
        )

    def test_purchase_order_list_can_search_by_supplier_name(self):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("api_purchase_order_list"),
            {
                "search": "API Test Supplier",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["count"],
            1,
        )

        self.assertEqual(
            len(data["results"]),
            1,
        )

        self.assertEqual(
            data["results"][0]["order_number"],
            "PO-API-001",
        )

class SalesOrderApiTests(TestCase):

    def setUp(self):

        self.user = get_user_model().objects.create_user(
            username="sales_api_user",
            password="test-password-123",
        )

        self.customer = Customer.objects.create(
            name="API Test Customer",
            email="customer@example.com",
            phone="9999999999",
            address="Test Address",
        )

        self.product = Product.objects.create(
            product_code="SOAPI001",
            name="Sales API Product",
            category="Electronics",
            description="Product for sales API test",
            quantity=20,
            purchase_price=Decimal("500.00"),
            selling_price=Decimal("800.00"),
            reorder_level=5,
            safety_stock=2,
            unit="PCS",
        )

        self.sales_order = SalesOrder.objects.create(
            customer=self.customer,
            created_by=self.user,
            order_number="SO-API-001",
            status="CONFIRMED",
            total_amount=Decimal("1600.00"),
            notes="API test sales order",
        )

        SalesOrderItem.objects.create(
            sales_order=self.sales_order,
            product=self.product,
            quantity=2,
            unit_price=Decimal("800.00"),
        )

    def test_sales_order_list_requires_authentication(self):

        response = self.client.get(
            reverse("api_sales_order_list")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_authenticated_user_can_view_sales_order_list(self):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("api_sales_order_list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["count"],
            1,
        )

        self.assertEqual(
            len(data["results"]),
            1,
        )

        self.assertEqual(
            data["results"][0]["order_number"],
            "SO-API-001",
        )

        self.assertEqual(
            data["results"][0]["customer_name"],
            "API Test Customer",
        )

    def test_sales_order_detail_includes_items(self):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse(
                "api_sales_order_detail",
                args=[self.sales_order.id],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["order_number"],
            "SO-API-001",
        )

        self.assertEqual(
            len(data["items"]),
            1,
        )

        self.assertEqual(
            data["items"][0]["product_code"],
            "SOAPI001",
        )

        self.assertEqual(
            data["items"][0]["product_name"],
            "Sales API Product",
        )

class FinanceApiTests(TestCase):

    def setUp(self):

        self.user = get_user_model().objects.create_user(
            username="finance_api_user",
            password="test-password-123",
        )

        self.customer = Customer.objects.create(
            name="Finance API Customer",
            email="finance-customer@example.com",
        )

        self.sales_order = SalesOrder.objects.create(
            customer=self.customer,
            created_by=self.user,
            order_number="SO-FIN-API-001",
            status="COMPLETED",
            total_amount=Decimal("2500.00"),
            completed_date=date(2026, 9, 14),
        )

        self.expense = Expense.objects.create(
            title="Finance API Expense",
            category="OFFICE",
            amount=Decimal("750.00"),
            expense_date=date(2026, 9, 14),
            reference_number="EXP-API-001",
            status="PENDING",
            created_by=self.user,
        )

        self.revenue = Revenue.objects.create(
            sales_order=self.sales_order,
            amount=Decimal("2500.00"),
            revenue_date=date(2026, 9, 14),
            reference_number="SO-FIN-API-001",
            created_by=self.user,
        )

    def test_expense_list_requires_authentication(self):

        response = self.client.get(
            reverse("api_expense_list")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_authenticated_user_can_view_expense_list(self):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("api_expense_list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["count"],
            1,
        )

        self.assertEqual(
            len(data["results"]),
            1,
        )

        self.assertEqual(
            data["results"][0]["reference_number"],
            "EXP-API-001",
        )

    def test_authenticated_user_can_view_expense_detail(self):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse(
                "api_expense_detail",
                args=[self.expense.id],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json()["title"],
            "Finance API Expense",
        )

    def test_authenticated_user_can_view_revenue_list(self):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("api_revenue_list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["count"],
            1,
        )

        self.assertEqual(
            len(data["results"]),
            1,
        )

        self.assertEqual(
            data["results"][0]["sales_order_number"],
            "SO-FIN-API-001",
        )

    def test_authenticated_user_can_view_revenue_detail(self):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse(
                "api_revenue_detail",
                args=[self.revenue.id],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json()["reference_number"],
            "SO-FIN-API-001",
        )

    def test_expense_list_can_search_by_reference_number(self):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("api_expense_list"),
            {
                "search": "EXP-API-001",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["count"],
            1,
        )

        self.assertEqual(
            len(data["results"]),
            1,
        )

        self.assertEqual(
            data["results"][0]["title"],
            "Finance API Expense",
        )

class HrApiTests(TestCase):

    def setUp(self):

        self.user = get_user_model().objects.create_user(
            username="hr_api_user",
            password="test-password-123",
        )

        self.department = Department.objects.create(
            name="Engineering",
            description="Engineering department",
        )

        self.employee = Employee.objects.create(
            employee_id="EMP-API-001",
            first_name="Test",
            last_name="Employee",
            email="employee-api@example.com",
            phone="9999999999",
            department=self.department,
            designation="Software Engineer",
            joining_date="2026-09-14",
            salary=Decimal("50000.00"),
            status="ACTIVE",
        )

    def test_employee_list_requires_authentication(self):

        response = self.client.get(
            reverse("api_employee_list")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_authenticated_user_can_view_department_list(self):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("api_department_list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["count"],
            1,
        )

        self.assertEqual(
            len(data["results"]),
            1,
        )

        self.assertEqual(
            data["results"][0]["name"],
            "Engineering",
        )

    def test_authenticated_user_can_view_employee_list(self):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("api_employee_list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["count"],
            1,
        )

        self.assertEqual(
            len(data["results"]),
            1,
        )

        self.assertEqual(
            data["results"][0]["employee_id"],
            "EMP-API-001",
        )

        self.assertEqual(
            data["results"][0]["department_name"],
            "Engineering",
        )

    def test_authenticated_user_can_view_employee_detail(self):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse(
                "api_employee_detail",
                args=[self.employee.id],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["first_name"],
            "Test",
        )

        self.assertEqual(
            data["designation"],
            "Software Engineer",
        )

    def test_employee_list_can_search_by_department(self):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("api_employee_list"),
            {
                "search": "Engineering",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["count"],
            1,
        )

        self.assertEqual(
            len(data["results"]),
            1,
        )

        self.assertEqual(
            data["results"][0]["employee_id"],
            "EMP-API-001",
        )

class DemandForecastApiTests(TestCase):

    def setUp(self):

        self.localdate_patcher = patch(
            "sales.forecasting.timezone.localdate",
            return_value=date(2026, 9, 18),
        )

        self.localdate_patcher.start()

        self.addCleanup(
            self.localdate_patcher.stop
        )

        self.user = get_user_model().objects.create_user(
            username="forecast_api_user",
            password="test-password-123",
        )

        self.product = Product.objects.create(
            product_code="FORECAST-API-001",
            name="Forecast API Product",
            category="Testing",
            description="Forecast API test product",
            quantity=25,
            purchase_price=Decimal("100.00"),
            selling_price=Decimal("150.00"),
            reorder_level=5,
            safety_stock=2,
            unit="PCS",
        )

        self.second_product = Product.objects.create(
            product_code="FORECAST-API-002",
            name="Second Forecast API Product",
            category="Testing",
            description="Second forecast API test product",
            quantity=40,
            purchase_price=Decimal("200.00"),
            selling_price=Decimal("300.00"),
            reorder_level=8,
            safety_stock=4,
            unit="PCS",
        )

    def test_demand_forecast_requires_authentication(self):

        response = self.client.get(
            reverse("api_demand_forecasts")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_authenticated_user_can_view_demand_forecasts(self):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("api_demand_forecasts")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["count"],
            2,
        )

        self.assertEqual(
            len(data["results"]),
            2,
        )

    def test_demand_forecast_response_structure(self):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("api_demand_forecasts")
        )

        data = response.json()

        self.assertIn(
            "count",
            data,
        )

        self.assertIn(
            "forecast_month",
            data,
        )

        self.assertIn(
            "results",
            data,
        )

        self.assertEqual(
            data["forecast_month"],
            "2026-09-01",
        )

    def test_demand_forecast_contains_expected_fields(self):

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse("api_demand_forecasts")
        )

        result = response.json()["results"][0]

        expected_fields = {
            "product_code",
            "product_name",
            "forecast_month",
            "predicted_demand",
            "method",
            "historical_months",
        }

        self.assertEqual(
            set(result.keys()),
            expected_fields,
        )

        self.assertGreaterEqual(
            result["predicted_demand"],
            0,
        )

        self.assertEqual(
            result["historical_months"],
            12,
        )

    def test_demand_forecast_api_is_read_only(self):

        self.client.force_login(
            self.user
        )

        response = self.client.post(
            reverse("api_demand_forecasts"),
            {},
        )

        self.assertEqual(
            response.status_code,
            405,
        )