from django.contrib import admin
from .models import User


class UserAdmin(admin. ModelAdmin):
    list_display = ['username', 'image', 'email', 'phone', 'bio']

admin.site.register(User, UserAdmin)
