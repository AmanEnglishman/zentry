from django.contrib.auth import get_user_model
from django.db.models import Count

from chat.models import Conversation


User = get_user_model()


def get_or_create_direct_conversation(user, participant):
    conversation = (
        Conversation.objects.annotate(participant_count=Count('participants', distinct=True))
        .filter(participants=user)
        .filter(participants=participant)
        .filter(participant_count=2)
        .first()
    )

    if conversation:
        return conversation, False

    conversation = Conversation.objects.create()
    conversation.participants.add(user, participant)
    return conversation, True
