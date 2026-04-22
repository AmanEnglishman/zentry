from django.contrib import admin

from posts.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'author__email')
    autocomplete_fields = ('author',)

# Register your models here.
