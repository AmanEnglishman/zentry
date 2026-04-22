from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from posts.models import Post
from social.models import Comment, Follow, Like


User = get_user_model()


class SocialApiTests(APITestCase):
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
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='strong-pass-123',
            is_staff=True,
        )
        self.post = Post.objects.create(author=self.author, content='Social post')

    def test_authenticated_user_can_comment(self):
        self.client.force_authenticate(user=self.reader)

        response = self.client.post('/api/comments/', {
            'post': self.post.id,
            'content': 'Nice one',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().user, self.reader)

    def test_comment_author_can_delete_comment(self):
        comment = Comment.objects.create(user=self.reader, post=self.post, content='Remove me')
        self.client.force_authenticate(user=self.reader)

        response = self.client.delete(f'/api/comments/{comment.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    def test_admin_can_delete_any_comment(self):
        comment = Comment.objects.create(user=self.reader, post=self.post, content='Moderate me')
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(f'/api/comments/{comment.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    def test_like_toggle_adds_and_removes_like(self):
        self.client.force_authenticate(user=self.reader)

        create_response = self.client.post('/api/like/', {'post': self.post.id}, format='json')
        remove_response = self.client.post('/api/like/', {'post': self.post.id}, format='json')

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(remove_response.status_code, status.HTTP_200_OK)
        self.assertFalse(remove_response.data['liked'])
        self.assertEqual(Like.objects.count(), 0)

    def test_direct_like_endpoint_rejects_duplicate_like(self):
        self.client.force_authenticate(user=self.reader)
        Like.objects.create(user=self.reader, post=self.post)

        response = self.client.post('/api/likes/', {'post': self.post.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Like.objects.count(), 1)

    def test_follow_toggle_adds_and_removes_follow(self):
        self.client.force_authenticate(user=self.reader)

        create_response = self.client.post('/api/follow/', {'following': self.author.id}, format='json')
        remove_response = self.client.post('/api/follow/', {'following': self.author.id}, format='json')

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(remove_response.status_code, status.HTTP_200_OK)
        self.assertFalse(remove_response.data['following'])
        self.assertEqual(Follow.objects.count(), 0)

    def test_user_cannot_follow_self(self):
        self.client.force_authenticate(user=self.reader)

        response = self.client.post('/api/follow/', {'following': self.reader.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Follow.objects.count(), 0)

    def test_follow_lists_are_public(self):
        Follow.objects.create(follower=self.reader, following=self.author)

        followers_response = self.client.get(f'/api/users/{self.author.id}/followers/')
        following_response = self.client.get(f'/api/users/{self.reader.id}/following/')

        self.assertEqual(followers_response.status_code, status.HTTP_200_OK)
        self.assertEqual(following_response.status_code, status.HTTP_200_OK)
        self.assertEqual(followers_response.data['count'], 1)
        self.assertEqual(following_response.data['count'], 1)

# Create your tests here.
