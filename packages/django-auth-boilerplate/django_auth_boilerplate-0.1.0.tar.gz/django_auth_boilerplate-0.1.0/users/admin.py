from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *
from django.utils.translation import gettext_lazy as _



class UserAdmin(BaseUserAdmin):
    model = User
    ordering = ['-created_at']
    list_display = ['id', 'email', 'first_name', 'last_name','is_active', 'is_staff', 'is_verified', 'is_superuser','auth_provider', 'get_groups_display', 'created_at']
    search_fields = ['id', 'email', 'first_name', 'last_name']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Important dates'), {'fields': ('created_at', 'last_login')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        (_('Authentication Provider'), {'fields': ('auth_provider',)}),
    )
    
    readonly_fields = ['created_at', 'last_login']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    def get_groups_display(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])

    get_groups_display.short_description = 'Groups'






admin.site.register(User, UserAdmin)
