from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.models import Notification
from notifications.serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Notification.objects.select_related('from_user', 'post').filter(user=self.request.user)


class NotificationMarkReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('patch',)

    def get_queryset(self):
        return Notification.objects.select_related('from_user', 'post').filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(is_read=True)


class NotificationMarkAllReadView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        updated = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'updated': updated}, status=status.HTTP_200_OK)

# Create your views here.
