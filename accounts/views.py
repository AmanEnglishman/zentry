from django.contrib.auth import get_user_model
from rest_framework import generics, permissions

from accounts.permissions import IsSelfOrReadOnly
from accounts.serializers import RegisterSerializer, UserProfileSerializer, UserPublicSerializer


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.user.is_authenticated and self.request.user.pk == self.get_object().pk:
            return UserProfileSerializer
        return UserPublicSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.AllowAny(),)
        return (permissions.IsAuthenticated(), IsSelfOrReadOnly())

    def perform_update(self, serializer):
        serializer.save()
