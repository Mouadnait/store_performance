from django.contrib import admin
from core.models import (
    Store, Product, ProductImages, Category, Tags,
    Client, ProductReview, Bill
)

class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'email', 'phone', 'city', 'country', 'status', 'created', 'sid']
    search_fields = ['name', 'email', 'city', 'country']
    list_filter = ['status', 'created']
    readonly_fields = ['sid', 'created', 'updated']
    prepopulated_fields = {'slug': ('name',)}

class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]
    list_display = ['user', 'title', 'product_image', 'price', 'stock', 'featured', 'product_status', 'pid']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category_image', 'cid']

class TagsAdmin(admin.ModelAdmin):
    list_display = ['name', 'created']
    search_fields = ['name']

class ClientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'address', 'city', 'country', 'gpt5_enabled', 'user', 'lid']

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'date']
    readonly_fields = ['date']

class BillAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'client', 'date', 'description', 'quantity', 'price', 'amount', 'total_price']

admin.site.register(Store, StoreAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(Bill, BillAdmin)
