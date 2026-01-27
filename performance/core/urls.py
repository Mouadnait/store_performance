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
    path("profile/", views.profile, name="profile"),
    # Bill actions
    path('bill/<int:bill_id>/edit/', views.edit_bill, name='edit_bill'),
    path('bill/<int:bill_id>/delete/', views.delete_bill, name='delete_bill'),
    path('bill/<int:bill_id>/print/', views.print_bill, name='print_bill'),
    path('bill/<int:bill_id>/duplicate/', views.duplicate_bill, name='duplicate_bill'),
    path('bill/<int:bill_id>/data/', views.get_bill_data, name='get_bill_data'),
    path('bill/<int:bill_id>/update/', views.update_bill_items, name='update_bill_items'),
    path('products/api/', views.products_api, name='products_api'),
    # Client actions
    path('update-client-picture/', views.update_client_picture, name='update_client_picture'),
]
