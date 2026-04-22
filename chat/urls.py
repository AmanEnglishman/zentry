from django.urls import path

from chat.views import ConversationListCreateView, ConversationMessageListView, ConversationReadView, MessageCreateView


urlpatterns = [
    path('conversations/', ConversationListCreateView.as_view(), name='conversation-list'),
    path('messages/', MessageCreateView.as_view(), name='message-create'),
    path('messages/<int:conversation_id>/', ConversationMessageListView.as_view(), name='message-list'),
    path('conversations/<int:conversation_id>/read/', ConversationReadView.as_view(), name='conversation-read'),
]
