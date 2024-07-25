from django.contrib import admin
from core.models import *

class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]
    list_display = ['user', 'title', 'product_image', 'price', 'stock', 'featured', 'product_status', 'pid']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category_image', 'cid']

class ClientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'profile_image', 'phone', 'address', 'city', 'country', 'postal_code', 'user', 'lid']

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'review', 'rating']

class BillAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'client', 'date', 'description', 'quantity', 'price', 'amount', 'total_price']

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(Bill, BillAdmin)
