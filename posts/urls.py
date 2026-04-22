from django.urls import path

from posts.views import FeedView, PostDetailView, PostListCreateView


urlpatterns = [
    path('posts/', PostListCreateView.as_view(), name='post-list'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('feed/', FeedView.as_view(), name='feed'),
]
