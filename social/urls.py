from django.urls import path

from social.views import (
    CommentCreateView,
    CommentDeleteView,
    FollowerListView,
    FollowingListView,
    FollowCreateView,
    FollowToggleView,
    LikeCreateView,
    LikeToggleView,
    PostCommentListView,
)


urlpatterns = [
    path('comments/', CommentCreateView.as_view(), name='comment-create'),
    path('comments/<int:pk>/', CommentDeleteView.as_view(), name='comment-delete'),
    path('posts/<int:post_id>/comments/', PostCommentListView.as_view(), name='post-comments'),
    path('likes/', LikeCreateView.as_view(), name='like-create'),
    path('like/', LikeToggleView.as_view(), name='like-toggle'),
    path('follows/', FollowCreateView.as_view(), name='follow-create'),
    path('follow/', FollowToggleView.as_view(), name='follow-toggle'),
    path('users/<int:user_id>/followers/', FollowerListView.as_view(), name='followers'),
    path('users/<int:user_id>/following/', FollowingListView.as_view(), name='following'),
]
