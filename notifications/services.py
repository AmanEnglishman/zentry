from notifications.models import Notification


def create_notification(*, user, from_user, notification_type, post=None):
    if user == from_user:
        return None

    return Notification.objects.create(
        user=user,
        from_user=from_user,
        type=notification_type,
        post=post,
    )
