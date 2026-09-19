from django.urls import path

from .views import (
    ApiStatusView,
    DemandForecastAPIView,
    DepartmentDetailAPIView,
    DepartmentListAPIView,
    EmployeeDetailAPIView,
    EmployeeListAPIView,
    ExpenseDetailAPIView,
    ExpenseListAPIView,
    ProductDetailAPIView,
    ProductListAPIView,
    PurchaseOrderDetailAPIView,
    PurchaseOrderListAPIView,
    RevenueDetailAPIView,
    RevenueListAPIView,
    SalesOrderDetailAPIView,
    SalesOrderListAPIView,
    ExpenseAnomalyAPIView,
    SupplierScoreAPIView,
    ReorderRecommendationAPIView,
)

urlpatterns = [
    path(
        "status/",
        ApiStatusView.as_view(),
        name="api_status",
    ),

    path(
        "demand-forecasts/",
        DemandForecastAPIView.as_view(),
        name="api_demand_forecasts",
    ),

    path(
        "expense-anomalies/",
        ExpenseAnomalyAPIView.as_view(),
        name="api_expense_anomalies",
    ),

    path(
        "products/",
        ProductListAPIView.as_view(),
        name="api_product_list",
    ),

    path(
        "products/<int:pk>/",
        ProductDetailAPIView.as_view(),
        name="api_product_detail",
    ),

    path(
        "purchase-orders/",
        PurchaseOrderListAPIView.as_view(),
        name="api_purchase_order_list",
    ),

    path(
        "purchase-orders/<int:pk>/",
        PurchaseOrderDetailAPIView.as_view(),
        name="api_purchase_order_detail",
    ),

    path(
        "sales-orders/",
        SalesOrderListAPIView.as_view(),
        name="api_sales_order_list",
    ),

    path(
        "sales-orders/<int:pk>/",
        SalesOrderDetailAPIView.as_view(),
        name="api_sales_order_detail",
    ),

    path(
        "expenses/",
        ExpenseListAPIView.as_view(),
        name="api_expense_list",
    ),

    path(
        "expenses/<int:pk>/",
        ExpenseDetailAPIView.as_view(),
        name="api_expense_detail",
    ),

    path(
        "revenues/",
        RevenueListAPIView.as_view(),
        name="api_revenue_list",
    ),

    path(
        "revenues/<int:pk>/",
        RevenueDetailAPIView.as_view(),
        name="api_revenue_detail",
    ),

    path(
        "departments/",
        DepartmentListAPIView.as_view(),
        name="api_department_list",
    ),
    
    path(
        "departments/<int:pk>/",
        DepartmentDetailAPIView.as_view(),
        name="api_department_detail",
    ),
    
    path(
        "employees/",
        EmployeeListAPIView.as_view(),
        name="api_employee_list",
    ),
    
    path(
        "employees/<int:pk>/",
        EmployeeDetailAPIView.as_view(),
        name="api_employee_detail",
    ),

    path(
        "supplier-scores/",
        SupplierScoreAPIView.as_view(),
        name="api_supplier_scores",
    ),

    path(
        "reorder-recommendations/",
        ReorderRecommendationAPIView.as_view(),
        name="api_reorder_recommendations",
    ),
]