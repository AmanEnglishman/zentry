from django.urls import path

from notifications.views import NotificationListView, NotificationMarkAllReadView, NotificationMarkReadView


urlpatterns = [
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification-read'),
    path('notifications/read-all/', NotificationMarkAllReadView.as_view(), name='notification-read-all'),
]
