from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter, SearchFilter

from finance.models import Expense, Revenue
from hr.models import Department, Employee
from inventory.models import Product
from procurement.models import PurchaseOrder
from sales.models import SalesOrder

from .serializers import (
    DepartmentSerializer,
    EmployeeSerializer,
    ExpenseSerializer,
    ProductSerializer,
    PurchaseOrderSerializer,
    RevenueSerializer,
    SalesOrderSerializer,
)

from .pagination import StandardResultsSetPagination


class ApiStatusView(APIView):

    def get(self, request):

        return Response(
            {
                "status": "ok",
                "message": "SmartERP API is running.",
                "user": request.user.username,
            }
        )

class ProductListAPIView(ListAPIView):

    queryset = Product.objects.all().order_by("name")
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination

    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "product_code",
        "name",
        "category",
        "description",
    ]

    ordering_fields = [
        "name",
        "product_code",
        "quantity",
        "purchase_price",
        "selling_price",
        "created_at",
    ]

    ordering = [
        "name",
    ]

class ProductDetailAPIView(RetrieveAPIView):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class PurchaseOrderListAPIView(ListAPIView):

    queryset = (
        PurchaseOrder.objects.select_related(
            "supplier",
            "created_by",
            "approved_by",
        )
        .prefetch_related(
            "items__product",
        )
        .order_by(
            "-order_date",
            "-id",
        )
    )

    serializer_class = PurchaseOrderSerializer
    pagination_class = StandardResultsSetPagination

    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "order_number",
        "supplier__name",
        "status",
        "notes",
    ]

    ordering_fields = [
        "order_number",
        "status",
        "order_date",
        "expected_delivery_date",
        "received_date",
        "total_amount",
        "created_at",
    ]

    ordering = [
        "-order_date",
        "-id",
    ]

class PurchaseOrderDetailAPIView(RetrieveAPIView):

    queryset = (
        PurchaseOrder.objects.select_related(
            "supplier",
            "created_by",
            "approved_by",
        )
        .prefetch_related(
            "items__product",
        )
    )

    serializer_class = PurchaseOrderSerializer

class SalesOrderListAPIView(ListAPIView):

    queryset = (
        SalesOrder.objects.select_related(
            "customer",
            "created_by",
        )
        .prefetch_related(
            "items__product",
        )
        .order_by(
            "-order_date",
            "-id",
        )
    )

    serializer_class = SalesOrderSerializer
    pagination_class = StandardResultsSetPagination

    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "order_number",
        "customer__name",
        "status",
        "notes",
    ]

    ordering_fields = [
        "order_number",
        "status",
        "order_date",
        "completed_date",
        "total_amount",
        "created_at",
    ]

    ordering = [
        "-order_date",
        "-id",
    ]


class SalesOrderDetailAPIView(RetrieveAPIView):

    queryset = (
        SalesOrder.objects.select_related(
            "customer",
            "created_by",
        )
        .prefetch_related(
            "items__product",
        )
    )

    serializer_class = SalesOrderSerializer

class ExpenseListAPIView(ListAPIView):

    queryset = (
        Expense.objects.select_related(
            "created_by",
            "reviewed_by",
            "purchase_order",
        )
        .order_by(
            "-expense_date",
            "-id",
        )
    )

    serializer_class = ExpenseSerializer
    pagination_class = StandardResultsSetPagination

    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "title",
        "reference_number",
        "category",
        "status",
        "description",
        "purchase_order__order_number",
    ]

    ordering_fields = [
        "title",
        "category",
        "status",
        "amount",
        "expense_date",
        "paid_at",
        "created_at",
    ]

    ordering = [
        "-expense_date",
        "-id",
    ]


class ExpenseDetailAPIView(RetrieveAPIView):

    queryset = Expense.objects.select_related(
        "created_by",
        "reviewed_by",
        "purchase_order",
    )

    serializer_class = ExpenseSerializer


class RevenueListAPIView(ListAPIView):

    queryset = (
        Revenue.objects.select_related(
            "sales_order",
            "created_by",
        )
        .order_by(
            "-revenue_date",
            "-id",
        )
    )

    serializer_class = RevenueSerializer
    pagination_class = StandardResultsSetPagination

    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "reference_number",
        "sales_order__order_number",
    ]

    ordering_fields = [
        "reference_number",
        "amount",
        "revenue_date",
        "created_at",
    ]

    ordering = [
        "-revenue_date",
        "-id",
    ]


class RevenueDetailAPIView(RetrieveAPIView):

    queryset = Revenue.objects.select_related(
        "sales_order",
        "created_by",
    )

    serializer_class = RevenueSerializer

class DepartmentListAPIView(ListAPIView):

    queryset = Department.objects.all().order_by("name")

    serializer_class = DepartmentSerializer
    pagination_class = StandardResultsSetPagination

    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "name",
        "description",
    ]

    ordering_fields = [
        "name",
    ]

    ordering = [
        "name",
    ]


class DepartmentDetailAPIView(RetrieveAPIView):

    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class EmployeeListAPIView(ListAPIView):

    queryset = (
        Employee.objects.select_related(
            "department",
        )
        .order_by(
            "employee_id",
        )
    )

    serializer_class = EmployeeSerializer
    pagination_class = StandardResultsSetPagination

    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "employee_id",
        "first_name",
        "last_name",
        "email",
        "designation",
        "status",
        "department__name",
    ]

    ordering_fields = [
        "employee_id",
        "first_name",
        "last_name",
        "joining_date",
        "salary",
        "status",
        "created_at",
    ]

    ordering = [
        "employee_id",
    ]


class EmployeeDetailAPIView(RetrieveAPIView):

    queryset = Employee.objects.select_related(
        "department",
    )

    serializer_class = EmployeeSerializer