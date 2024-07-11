from django.contrib import admin
from .models import User, Client


class UserAdmin(admin. ModelAdmin):
    list_display = ['username', 'email', 'bio']
    
class ClientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'address', 'city', 'country', 'postal_code', 'store_id']

admin.site.register(User, UserAdmin)
admin.site.register(Client, ClientAdmin)
