from rest_framework import serializers

from accounts.serializers import UserPublicSerializer
from posts.models import Post


class PostSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Post
        fields = (
            'id',
            'author',
            'content',
            'image',
            'likes_count',
            'comments_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError('Post content cannot be empty.')
        return value
