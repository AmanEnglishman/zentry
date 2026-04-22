from rest_framework import serializers

from accounts.serializers import UserPublicSerializer
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    from_user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ('id', 'from_user', 'type', 'post', 'is_read', 'created_at')
        read_only_fields = ('id', 'from_user', 'type', 'post', 'created_at')
