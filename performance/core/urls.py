from django.urls import path
from core import views

app_name = "core"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("analytics/", views.analytics, name="analytics"),
    path("bills/", views.bills, name="bills"),
    path("clients/", views.clients, name="clients"),
    path("products/", views.products, name="products"),
    path("reports/", views.reports, name="reports"),
    path("settings/", views.settings, name="settings"),
]
