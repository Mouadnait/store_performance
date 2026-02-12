from django.contrib import admin
from .models import User
from core.models import Store


class StoreInline(admin.TabularInline):
    model = Store
    extra = 1
    fields = ['name', 'slug', 'status', 'city', 'country', 'created']
    readonly_fields = ['created']
    show_change_link = True
    ordering = ['-created']


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone', 'store_count', 'first_store']
    search_fields = ['username', 'email', 'phone']
    inlines = [StoreInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(id=request.user.id)

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return obj is None or obj == request.user

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return obj == request.user

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser and super().has_delete_permission(request, obj)

    def store_count(self, obj):
        return obj.stores.count()
    store_count.short_description = 'Stores'

    def first_store(self, obj):
        store = obj.stores.first()
        return store.name if store else '-'
    first_store.short_description = 'Primary Store'


admin.site.register(User, UserAdmin)
