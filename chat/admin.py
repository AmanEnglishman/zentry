from django.contrib import admin

from chat.models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    autocomplete_fields = ('sender',)
    readonly_fields = ('created_at',)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at')
    search_fields = ('id', 'participants__username', 'participants__email')
    filter_horizontal = ('participants',)
    inlines = (MessageInline,)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('content', 'sender__username', 'sender__email')
    autocomplete_fields = ('conversation', 'sender')

# Register your models here.
