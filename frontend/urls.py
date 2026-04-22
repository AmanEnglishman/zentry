from django.urls import path

from frontend import views


app_name = 'frontend'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('posts/create/', views.create_post_view, name='post-create'),
    path('posts/<int:post_id>/delete/', views.delete_post_view, name='post-delete'),
    path('posts/<int:post_id>/like/', views.like_post_view, name='post-like'),
    path('posts/<int:post_id>/comment/', views.comment_post_view, name='post-comment'),
    path('comments/<int:comment_id>/delete/', views.delete_comment_view, name='comment-delete'),
    path('users/<int:user_id>/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile_view, name='profile-update'),
    path('users/<int:user_id>/follow/', views.follow_user_view, name='follow'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/read/', views.mark_notifications_read_view, name='notifications-read'),
    path('conversations/', views.conversations_view, name='conversations'),
    path('conversations/<int:conversation_id>/', views.conversation_view, name='conversation'),
]
