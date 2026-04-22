from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from notifications.models import Notification
from posts.models import Post


User = get_user_model()


class NotificationApiTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='strong-pass-123',
        )
        self.reader = User.objects.create_user(
            username='reader',
            email='reader@example.com',
            password='strong-pass-123',
        )
        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='strong-pass-123',
        )
        self.post = Post.objects.create(author=self.author, content='Notify me')

    def test_comment_creates_notification_for_post_author(self):
        self.client.force_authenticate(user=self.reader)

        response = self.client.post('/api/comments/', {
            'post': self.post.id,
            'content': 'Nice',
        }, format='json')

        notification = Notification.objects.get()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(notification.user, self.author)
        self.assertEqual(notification.from_user, self.reader)
        self.assertEqual(notification.type, Notification.Type.COMMENT)
        self.assertEqual(notification.post, self.post)

    def test_like_creates_notification_for_post_author(self):
        self.client.force_authenticate(user=self.reader)

        response = self.client.post('/api/like/', {'post': self.post.id}, format='json')

        notification = Notification.objects.get()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(notification.user, self.author)
        self.assertEqual(notification.type, Notification.Type.LIKE)
        self.assertEqual(notification.post, self.post)

    def test_follow_creates_notification_for_followed_user(self):
        self.client.force_authenticate(user=self.reader)

        response = self.client.post('/api/follow/', {'following': self.author.id}, format='json')

        notification = Notification.objects.get()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(notification.user, self.author)
        self.assertEqual(notification.from_user, self.reader)
        self.assertEqual(notification.type, Notification.Type.FOLLOW)
        self.assertIsNone(notification.post)

    def test_self_action_does_not_create_notification(self):
        self.client.force_authenticate(user=self.author)

        response = self.client.post('/api/like/', {'post': self.post.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), 0)

    def test_user_can_list_only_own_notifications(self):
        own_notification = Notification.objects.create(
            user=self.author,
            from_user=self.reader,
            type=Notification.Type.LIKE,
            post=self.post,
        )
        Notification.objects.create(
            user=self.other_user,
            from_user=self.reader,
            type=Notification.Type.FOLLOW,
        )
        self.client.force_authenticate(user=self.author)

        response = self.client.get('/api/notifications/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], own_notification.id)

    def test_user_can_mark_own_notification_as_read(self):
        notification = Notification.objects.create(
            user=self.author,
            from_user=self.reader,
            type=Notification.Type.LIKE,
            post=self.post,
        )
        self.client.force_authenticate(user=self.author)

        response = self.client.patch(f'/api/notifications/{notification.id}/read/', {}, format='json')

        notification.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(notification.is_read)

    def test_user_cannot_mark_other_users_notification_as_read(self):
        notification = Notification.objects.create(
            user=self.author,
            from_user=self.reader,
            type=Notification.Type.LIKE,
            post=self.post,
        )
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(f'/api/notifications/{notification.id}/read/', {}, format='json')

        notification.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(notification.is_read)

    def test_user_can_mark_all_notifications_as_read(self):
        Notification.objects.create(user=self.author, from_user=self.reader, type=Notification.Type.LIKE, post=self.post)
        Notification.objects.create(user=self.author, from_user=self.reader, type=Notification.Type.COMMENT, post=self.post)
        Notification.objects.create(user=self.other_user, from_user=self.reader, type=Notification.Type.FOLLOW)
        self.client.force_authenticate(user=self.author)

        response = self.client.post('/api/notifications/read-all/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['updated'], 2)
        self.assertFalse(Notification.objects.filter(user=self.author, is_read=False).exists())
        self.assertTrue(Notification.objects.filter(user=self.other_user, is_read=False).exists())

# Create your tests here.
