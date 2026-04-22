from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import Conversation, Message
from chat.serializers import ConversationCreateSerializer, ConversationSerializer, MessageSerializer


class ConversationListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return (
            Conversation.objects.prefetch_related('participants', 'messages')
            .filter(participants=self.request.user)
            .order_by('-updated_at')
        )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ConversationCreateSerializer
        return ConversationSerializer


class MessageCreateView(generics.CreateAPIView):
    queryset = Message.objects.select_related('conversation', 'sender').all()
    serializer_class = MessageSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        message = serializer.save(sender=self.request.user)
        message.conversation.save(update_fields=('updated_at',))


class ConversationMessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        conversation = get_object_or_404(
            Conversation.objects.filter(participants=self.request.user),
            pk=self.kwargs['conversation_id'],
        )
        return conversation.messages.select_related('sender', 'conversation').order_by('created_at')


class ConversationReadView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, conversation_id):
        conversation = get_object_or_404(
            Conversation.objects.filter(participants=request.user),
            pk=conversation_id,
        )
        updated = conversation.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)
        return Response({'updated': updated}, status=status.HTTP_200_OK)

# Create your views here.
