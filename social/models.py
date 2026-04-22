from django.conf import settings
from django.db import models

from posts.models import Post


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)
        indexes = [
            models.Index(fields=('post', 'created_at')),
            models.Index(fields=('user', '-created_at')),
        ]

    def __str__(self):
        return f'{self.user_id} on {self.post_id}: {self.content[:40]}'


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('user', 'post'), name='unique_like_per_user_post'),
        ]
        indexes = [
            models.Index(fields=('post', '-created_at')),
            models.Index(fields=('user', '-created_at')),
        ]

    def __str__(self):
        return f'{self.user_id} likes {self.post_id}'


class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following_links')
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='follower_links')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('follower', 'following'), name='unique_follow_pair'),
            models.CheckConstraint(
                condition=~models.Q(follower=models.F('following')),
                name='prevent_self_follow',
            ),
        ]
        indexes = [
            models.Index(fields=('follower', '-created_at')),
            models.Index(fields=('following', '-created_at')),
        ]

    def __str__(self):
        return f'{self.follower_id} follows {self.following_id}'

# Create your models here.
