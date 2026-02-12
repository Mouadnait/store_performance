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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.owner = request.user
        elif not obj.owner_id:
            obj.owner = request.user
        super().save_model(request, obj, form, change)

class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]
    list_display = ['user', 'store', 'title', 'product_image', 'price', 'stock', 'featured', 'product_status', 'pid']
    list_filter = ['store', 'product_status', 'featured']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.user = request.user
            if not obj.store_id:
                first_store = request.user.stores.first()
                obj.store = first_store
        super().save_model(request, obj, form, change)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category_image', 'cid']

class TagsAdmin(admin.ModelAdmin):
    list_display = ['name', 'created']
    search_fields = ['name']

class ClientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'address', 'city', 'country', 'store', 'gpt5_enabled', 'user', 'lid']
    list_filter = ['store', 'gpt5_enabled']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.user = request.user
            if not obj.store_id:
                obj.store = request.user.stores.first()
        super().save_model(request, obj, form, change)

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'date']
    readonly_fields = ['date']

class BillAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'store', 'client', 'date', 'description', 'quantity', 'price', 'amount', 'total_price']
    list_filter = ['store', 'date']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(store_name=request.user)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.store_name = request.user
            if not obj.store_id:
                obj.store = request.user.stores.first()
        elif not obj.store and obj.store_name:
            # fallback for superuser: align store with store_name owner if available
            first_store = obj.store_name.stores.first()
            if first_store:
                obj.store = first_store
        super().save_model(request, obj, form, change)

admin.site.register(Store, StoreAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(Bill, BillAdmin)
