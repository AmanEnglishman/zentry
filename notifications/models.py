from django.conf import settings
from django.db import models

from posts.models import Post


class Notification(models.Model):
    class Type(models.TextChoices):
        LIKE = 'like', 'Like'
        COMMENT = 'comment', 'Comment'
        FOLLOW = 'follow', 'Follow'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
    )
    type = models.CharField(max_length=20, choices=Type.choices)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='notifications', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=('user', 'is_read', '-created_at')),
            models.Index(fields=('from_user', '-created_at')),
        ]

    def __str__(self):
        return f'{self.type} from {self.from_user_id} to {self.user_id}'

# Create your models here.
