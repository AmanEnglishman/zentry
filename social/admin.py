from django.contrib import admin

from social.models import Comment, Follow, Like


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__username', 'post__content')
    autocomplete_fields = ('user', 'post')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    list_filter = ('created_at',)
    autocomplete_fields = ('user', 'post')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'following', 'created_at')
    list_filter = ('created_at',)
    autocomplete_fields = ('follower', 'following')

# Register your models here.
