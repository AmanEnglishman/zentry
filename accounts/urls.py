from django.urls import path

from accounts.views import RegisterView, UserDetailView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
