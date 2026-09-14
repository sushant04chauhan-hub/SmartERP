from rest_framework import serializers

from inventory.models import Product
from finance.models import Expense, Revenue
from hr.models import Department, Employee

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

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product

        fields = [
            "id",
            "product_code",
            "name",
            "category",
            "description",
            "quantity",
            "purchase_price",
            "selling_price",
            "reorder_level",
            "safety_stock",
            "unit",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "quantity",
            "created_at",
            "updated_at",
        ]

class SupplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = Supplier

        fields = [
            "id",
            "name",
            "contact_person",
            "email",
            "phone",
            "address",
            "is_active",
        ]


class PurchaseOrderItemSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    product_code = serializers.CharField(
        source="product.product_code",
        read_only=True,
    )

    total_price = serializers.ReadOnlyField()

    class Meta:
        model = PurchaseOrderItem

        fields = [
            "id",
            "product",
            "product_code",
            "product_name",
            "quantity",
            "unit_price",
            "total_price",
        ]


class PurchaseOrderSerializer(serializers.ModelSerializer):

    supplier_name = serializers.CharField(
        source="supplier.name",
        read_only=True,
    )

    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    approved_by_username = serializers.CharField(
        source="approved_by.username",
        read_only=True,
    )

    items = PurchaseOrderItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = PurchaseOrder

        fields = [
            "id",
            "order_number",
            "supplier",
            "supplier_name",
            "status",
            "order_date",
            "expected_delivery_date",
            "received_date",
            "total_amount",
            "notes",
            "created_by_username",
            "approved_by_username",
            "items",
            "created_at",
            "updated_at",
        ]

class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer

        fields = [
            "id",
            "name",
            "email",
            "phone",
            "address",
            "is_active",
            "created_at",
            "updated_at",
        ]


class SalesOrderItemSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    product_code = serializers.CharField(
        source="product.product_code",
        read_only=True,
    )

    total_price = serializers.ReadOnlyField()

    class Meta:
        model = SalesOrderItem

        fields = [
            "id",
            "product",
            "product_code",
            "product_name",
            "quantity",
            "unit_price",
            "total_price",
        ]


class SalesOrderSerializer(serializers.ModelSerializer):

    customer_name = serializers.CharField(
        source="customer.name",
        read_only=True,
    )

    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    items = SalesOrderItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = SalesOrder

        fields = [
            "id",
            "order_number",
            "customer",
            "customer_name",
            "status",
            "order_date",
            "completed_date",
            "total_amount",
            "notes",
            "created_by_username",
            "items",
            "created_at",
            "updated_at",
        ]

class ExpenseSerializer(serializers.ModelSerializer):

    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    reviewed_by_username = serializers.CharField(
        source="reviewed_by.username",
        read_only=True,
    )

    purchase_order_number = serializers.CharField(
        source="purchase_order.order_number",
        read_only=True,
    )

    class Meta:
        model = Expense

        fields = [
            "id",
            "title",
            "category",
            "amount",
            "expense_date",
            "description",
            "reference_number",
            "status",
            "payment_method",
            "purchase_order",
            "purchase_order_number",
            "created_by_username",
            "reviewed_by_username",
            "reviewed_at",
            "paid_at",
            "created_at",
            "updated_at",
        ]


class RevenueSerializer(serializers.ModelSerializer):

    sales_order_number = serializers.CharField(
        source="sales_order.order_number",
        read_only=True,
    )

    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    class Meta:
        model = Revenue

        fields = [
            "id",
            "sales_order",
            "sales_order_number",
            "amount",
            "revenue_date",
            "reference_number",
            "created_by_username",
            "created_at",
            "updated_at",
        ]

class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department

        fields = [
            "id",
            "name",
            "description",
        ]


class EmployeeSerializer(serializers.ModelSerializer):

    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )

    class Meta:
        model = Employee

        fields = [
            "id",
            "employee_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "department",
            "department_name",
            "designation",
            "joining_date",
            "salary",
            "status",
            "created_at",
            "updated_at",
        ]