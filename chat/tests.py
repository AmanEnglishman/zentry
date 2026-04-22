from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from chat.models import Conversation, Message


User = get_user_model()


class ChatApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='sender',
            email='sender@example.com',
            password='strong-pass-123',
        )
        self.recipient = User.objects.create_user(
            username='recipient',
            email='recipient@example.com',
            password='strong-pass-123',
        )
        self.stranger = User.objects.create_user(
            username='stranger',
            email='stranger@example.com',
            password='strong-pass-123',
        )

    def test_user_can_create_direct_conversation(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post('/api/conversations/', {'participant': self.recipient.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conversation.objects.count(), 1)
        self.assertEqual(Conversation.objects.first().participants.count(), 2)

    def test_creating_existing_direct_conversation_returns_same_conversation(self):
        self.client.force_authenticate(user=self.user)

        first_response = self.client.post('/api/conversations/', {'participant': self.recipient.id}, format='json')
        second_response = self.client.post('/api/conversations/', {'participant': self.recipient.id}, format='json')

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(first_response.data['id'], second_response.data['id'])
        self.assertEqual(Conversation.objects.count(), 1)

    def test_user_cannot_create_conversation_with_self(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post('/api/conversations/', {'participant': self.user.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Conversation.objects.count(), 0)

    def test_user_lists_only_own_conversations(self):
        own_conversation = Conversation.objects.create()
        own_conversation.participants.add(self.user, self.recipient)
        other_conversation = Conversation.objects.create()
        other_conversation.participants.add(self.recipient, self.stranger)
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/conversations/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], own_conversation.id)

    def test_participant_can_send_message(self):
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user, self.recipient)
        self.client.force_authenticate(user=self.user)

        response = self.client.post('/api/messages/', {
            'conversation': conversation.id,
            'content': 'Hello',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.first().sender, self.user)

    def test_non_participant_cannot_send_message(self):
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user, self.recipient)
        self.client.force_authenticate(user=self.stranger)

        response = self.client.post('/api/messages/', {
            'conversation': conversation.id,
            'content': 'Nope',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Message.objects.count(), 0)

    def test_participant_can_read_conversation_history(self):
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user, self.recipient)
        message = Message.objects.create(conversation=conversation, sender=self.user, content='History')
        self.client.force_authenticate(user=self.recipient)

        response = self.client.get(f'/api/messages/{conversation.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], message.id)

    def test_non_participant_cannot_read_conversation_history(self):
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user, self.recipient)
        self.client.force_authenticate(user=self.stranger)

        response = self.client.get(f'/api/messages/{conversation.id}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_participant_can_mark_incoming_messages_as_read(self):
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user, self.recipient)
        incoming = Message.objects.create(conversation=conversation, sender=self.recipient, content='Read me')
        own = Message.objects.create(conversation=conversation, sender=self.user, content='Mine')
        self.client.force_authenticate(user=self.user)

        response = self.client.post(f'/api/conversations/{conversation.id}/read/')

        incoming.refresh_from_db()
        own.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['updated'], 1)
        self.assertTrue(incoming.is_read)
        self.assertFalse(own.is_read)

# Create your tests here.
