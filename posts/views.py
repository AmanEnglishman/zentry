from rest_framework import generics, permissions

from posts.models import Post
from posts.permissions import IsAuthorOrReadOnly
from posts.serializers import PostSerializer
from social.models import Follow


class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.select_related('author').all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.select_related('author').all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)


class FeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        following_ids = Follow.objects.filter(
            follower=self.request.user,
        ).values_list('following_id', flat=True)

        return Post.objects.select_related('author').filter(
            author_id__in=following_ids,
        ).order_by('-created_at')
