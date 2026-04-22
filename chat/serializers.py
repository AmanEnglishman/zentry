from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.serializers import UserPublicSerializer
from chat.models import Conversation, Message
from chat.services import get_or_create_direct_conversation


User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    sender = UserPublicSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'conversation', 'sender', 'content', 'created_at', 'is_read')
        read_only_fields = ('id', 'sender', 'created_at', 'is_read')

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError('Message content cannot be empty.')
        return value

    def validate_conversation(self, conversation):
        user = self.context['request'].user
        if not conversation.participants.filter(id=user.id).exists():
            raise serializers.ValidationError('You are not a participant of this conversation.')
        return conversation


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserPublicSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ('id', 'participants', 'last_message', 'created_at', 'updated_at')
        read_only_fields = fields

    def get_last_message(self, obj):
        message = obj.messages.order_by('-created_at').first()
        if not message:
            return None
        return MessageSerializer(message, context=self.context).data


class ConversationCreateSerializer(serializers.Serializer):
    participant = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def validate_participant(self, participant):
        if participant == self.context['request'].user:
            raise serializers.ValidationError('You cannot create a conversation with yourself.')
        return participant

    def create(self, validated_data):
        conversation, _ = get_or_create_direct_conversation(
            self.context['request'].user,
            validated_data['participant'],
        )
        return conversation

    def to_representation(self, instance):
        return ConversationSerializer(instance, context=self.context).data
