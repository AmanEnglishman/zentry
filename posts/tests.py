from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from posts.models import Post
from social.models import Follow


User = get_user_model()


class PostApiTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='strong-pass-123',
        )
        self.other_user = User.objects.create_user(
            username='reader',
            email='reader@example.com',
            password='strong-pass-123',
        )

    def test_authenticated_user_can_create_post(self):
        self.client.force_authenticate(user=self.author)

        response = self.client.post('/api/posts/', {'content': 'First post'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.first().author, self.author)

    def test_anonymous_user_can_list_posts(self):
        Post.objects.create(author=self.author, content='Public post')

        response = self.client.get('/api/posts/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_only_author_can_delete_post(self):
        post = Post.objects.create(author=self.author, content='Owned post')
        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(f'/api/posts/{post.id}/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Post.objects.filter(id=post.id).exists())

    def test_feed_requires_authentication(self):
        response = self.client.get('/api/feed/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_feed_contains_only_followed_users_posts(self):
        followed_user = User.objects.create_user(
            username='followed',
            email='followed@example.com',
            password='strong-pass-123',
        )
        unfollowed_user = User.objects.create_user(
            username='unfollowed',
            email='unfollowed@example.com',
            password='strong-pass-123',
        )
        Follow.objects.create(follower=self.other_user, following=followed_user)
        followed_post = Post.objects.create(author=followed_user, content='In feed')
        Post.objects.create(author=unfollowed_user, content='Not in feed')
        Post.objects.create(author=self.other_user, content='Own post is not followed feed')
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get('/api/feed/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], followed_post.id)

    def test_feed_is_sorted_by_created_at_desc(self):
        followed_user = User.objects.create_user(
            username='followed',
            email='followed@example.com',
            password='strong-pass-123',
        )
        Follow.objects.create(follower=self.other_user, following=followed_user)
        older_post = Post.objects.create(author=followed_user, content='Older')
        newer_post = Post.objects.create(author=followed_user, content='Newer')
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get('/api/feed/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], newer_post.id)
        self.assertEqual(response.data['results'][1]['id'], older_post.id)
