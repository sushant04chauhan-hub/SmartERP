from django.urls import path

from audit.views import AuditLogListAPIView

from .dashboard import DashboardAPIView

from .views import (
    ApiStatusView,
    DemandForecastAPIView,
    DepartmentDetailAPIView,
    DepartmentListAPIView,
    EmployeeDetailAPIView,
    EmployeeListAPIView,
    ExpenseAnomalyAPIView,
    ExpenseDetailAPIView,
    ExpenseListAPIView,
    ProductDetailAPIView,
    ProductListAPIView,
    PurchaseOrderDetailAPIView,
    PurchaseOrderListAPIView,
    ReorderRecommendationAPIView,
    RevenueDetailAPIView,
    RevenueListAPIView,
    SalesOrderDetailAPIView,
    SalesOrderListAPIView,
    SupplierScoreAPIView,
)

from notifications.views import (
    NotificationListAPIView,
    NotificationMarkAllReadAPIView,
    NotificationMarkReadAPIView,
    NotificationUnreadCountAPIView,
)

urlpatterns = [

    path(
        "status/",
        ApiStatusView.as_view(),
        name="api_status",
    ),

    path(
        "dashboard/",
        DashboardAPIView.as_view(),
        name="api_dashboard",
    ),

    path(
        "audit-logs/",
        AuditLogListAPIView.as_view(),
        name="api_audit_logs",
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

    path(
        "notifications/",
        NotificationListAPIView.as_view(),
        name="api_notification_list",
    ),

    path(
        "notifications/unread-count/",
        NotificationUnreadCountAPIView.as_view(),
        name="api_notification_unread_count",
    ),

    path(
        "notifications/<int:pk>/read/",
        NotificationMarkReadAPIView.as_view(),
        name="api_notification_mark_read",
    ),

    path(
        "notifications/mark-all-read/",
        NotificationMarkAllReadAPIView.as_view(),
        name="api_notification_mark_all_read",
    ),
]