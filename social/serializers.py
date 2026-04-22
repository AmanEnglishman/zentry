from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.serializers import UserPublicSerializer
from social.models import Comment, Follow, Like


User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'user', 'post', 'content', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError('Comment content cannot be empty.')
        return value


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('id', 'user', 'post', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')

    def validate_post(self, post):
        user = self.context['request'].user
        if Like.objects.filter(user=user, post=post).exists():
            raise serializers.ValidationError('You already liked this post.')
        return post


class FollowSerializer(serializers.ModelSerializer):
    follower = UserPublicSerializer(read_only=True)
    following = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = ('id', 'follower', 'following', 'created_at')
        read_only_fields = ('id', 'follower', 'created_at')

    def validate_following(self, following):
        follower = self.context['request'].user
        if follower == following:
            raise serializers.ValidationError('You cannot follow yourself.')
        if Follow.objects.filter(follower=follower, following=following).exists():
            raise serializers.ValidationError('You already follow this user.')
        return following


class FollowListSerializer(serializers.ModelSerializer):
    follower = UserPublicSerializer(read_only=True)
    following = UserPublicSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ('id', 'follower', 'following', 'created_at')
        read_only_fields = fields
