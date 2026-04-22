from django.contrib import admin

from notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'from_user', 'type', 'post', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__username', 'from_user__username', 'post__content')
    autocomplete_fields = ('user', 'from_user', 'post')

# Register your models here.
