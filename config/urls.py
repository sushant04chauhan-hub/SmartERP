"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("hr/", include("hr.urls")),
    path("inventory/", include("inventory.urls")),
    path("procurement/", include("procurement.urls")),
    path("finance/", include("finance.urls")),
    path("sales/", include("sales.urls"),),
]