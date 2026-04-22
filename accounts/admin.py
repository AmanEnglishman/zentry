from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('id', 'username', 'email', 'is_staff', 'created_at')
    search_fields = ('username', 'email')
    ordering = ('id',)
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('bio', 'avatar')}),
    )

# Register your models here.
