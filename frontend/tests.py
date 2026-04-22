from django.contrib.auth import get_user_model
from django.test import TestCase

from chat.models import Conversation, Message
from posts.models import Post


User = get_user_model()


class FrontendSmokeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='webuser',
            email='webuser@example.com',
            password='strong-pass-123',
        )
        self.other = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='strong-pass-123',
        )
        self.post = Post.objects.create(author=self.user, content='Hello web')

    def test_public_pages_render(self):
        for path in ('/', '/login/', '/register/', f'/users/{self.user.id}/'):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)

    def test_authenticated_pages_render(self):
        self.client.force_login(self.user)

        for path in ('/', f'/users/{self.user.id}/', '/notifications/', '/conversations/'):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)

    def test_conversation_page_renders(self):
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user, self.other)
        Message.objects.create(conversation=conversation, sender=self.other, content='Hi')
        self.client.force_login(self.user)

        response = self.client.get(f'/conversations/{conversation.id}/')

        self.assertEqual(response.status_code, 200)

# Create your tests here.
