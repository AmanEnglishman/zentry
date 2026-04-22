from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.models import Notification
from notifications.services import create_notification
from posts.models import Post
from social.models import Comment, Follow, Like
from social.permissions import IsCommentAuthorOrAdmin
from social.serializers import CommentSerializer, FollowListSerializer, FollowSerializer, LikeSerializer


User = get_user_model()


class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.select_related('user', 'post').all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        comment = serializer.save(user=self.request.user)
        create_notification(
            user=comment.post.author,
            from_user=self.request.user,
            notification_type=Notification.Type.COMMENT,
            post=comment.post,
        )


class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.select_related('user', 'post').all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated, IsCommentAuthorOrAdmin)


class PostCommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return Comment.objects.select_related('user').filter(post_id=self.kwargs['post_id'])


class LikeCreateView(generics.CreateAPIView):
    queryset = Like.objects.select_related('user', 'post').all()
    serializer_class = LikeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        like = serializer.save(user=self.request.user)
        create_notification(
            user=like.post.author,
            from_user=self.request.user,
            notification_type=Notification.Type.LIKE,
            post=like.post,
        )


class LikeToggleView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        post_id = request.data.get('post')
        post = get_object_or_404(Post, pk=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if created:
            create_notification(
                user=post.author,
                from_user=request.user,
                notification_type=Notification.Type.LIKE,
                post=post,
            )
            return Response(
                {'detail': 'Post liked.', 'liked': True, 'like_id': like.id},
                status=status.HTTP_201_CREATED,
            )

        like.delete()
        return Response({'detail': 'Like removed.', 'liked': False}, status=status.HTTP_200_OK)


class FollowCreateView(generics.CreateAPIView):
    queryset = Follow.objects.select_related('follower', 'following').all()
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        follow = serializer.save(follower=self.request.user)
        create_notification(
            user=follow.following,
            from_user=self.request.user,
            notification_type=Notification.Type.FOLLOW,
        )


class FollowToggleView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        following_id = request.data.get('following')
        following = get_object_or_404(User, pk=following_id)

        if following == request.user:
            return Response({'following': ['You cannot follow yourself.']}, status=status.HTTP_400_BAD_REQUEST)

        follow, created = Follow.objects.get_or_create(follower=request.user, following=following)
        if created:
            create_notification(
                user=following,
                from_user=request.user,
                notification_type=Notification.Type.FOLLOW,
            )
            return Response(
                {'detail': 'User followed.', 'following': True, 'follow_id': follow.id},
                status=status.HTTP_201_CREATED,
            )

        follow.delete()
        return Response({'detail': 'User unfollowed.', 'following': False}, status=status.HTTP_200_OK)


class FollowerListView(generics.ListAPIView):
    serializer_class = FollowListSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return Follow.objects.select_related('follower', 'following').filter(
            following_id=self.kwargs['user_id'],
        ).order_by('-created_at')


class FollowingListView(generics.ListAPIView):
    serializer_class = FollowListSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return Follow.objects.select_related('follower', 'following').filter(
            follower_id=self.kwargs['user_id'],
        ).order_by('-created_at')

# Create your views here.
