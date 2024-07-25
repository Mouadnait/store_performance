from django.urls import path
from core import views

app_name = "core"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("analytics/", views.analytics, name="analytics"),
    path("create-bill/", views.create_bill, name="create-bill"),
    path("clients/", views.clients, name="clients"),
    path('client/<lid>/', views.client_detail, name='client_detail'),
    path("products/", views.products, name="products"),
    path("reports/", views.reports, name="reports"),
    path("settings/", views.settings, name="settings"),
]
