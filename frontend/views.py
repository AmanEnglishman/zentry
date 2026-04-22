from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken

from chat.models import Conversation, Message
from chat.services import get_or_create_direct_conversation
from frontend.forms import CommentForm, ConversationForm, LoginForm, MessageForm, PostForm, ProfileForm, RegisterForm
from notifications.models import Notification
from notifications.services import create_notification
from posts.models import Post
from social.models import Comment, Follow, Like


User = get_user_model()


def register_view(request):
    if request.user.is_authenticated:
        return redirect('frontend:home')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Welcome to Zentry.')
        return redirect('frontend:home')

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('frontend:home')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get('next') or 'frontend:home')

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('frontend:login')


def home_view(request):
    posts = (
        Post.objects.select_related('author')
        .prefetch_related('comments__user', 'likes')
        .annotate(likes_total=Count('likes', distinct=True), comments_total=Count('comments', distinct=True))
    )

    title = 'Explore'
    if request.user.is_authenticated:
        following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
        feed_posts = posts.filter(author_id__in=following_ids)
        posts = feed_posts if feed_posts.exists() else posts
        title = 'Feed' if feed_posts.exists() else 'Explore'

    context = {
        'title': title,
        'posts': posts.order_by('-created_at')[:60],
        'post_form': PostForm(),
        'comment_form': CommentForm(),
        **viewer_state(request.user),
    }
    return render(request, 'frontend/home.html', context)


@login_required
def create_post_view(request):
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        messages.success(request, 'Post published.')
    else:
        messages.error(request, 'Post text cannot be empty.')
    return redirect(request.POST.get('next') or 'frontend:home')


@login_required
def delete_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()
    messages.success(request, 'Post deleted.')
    return redirect(request.POST.get('next') or 'frontend:home')


@login_required
def like_post_view(request, post_id):
    post = get_object_or_404(Post.objects.select_related('author'), id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if created:
        create_notification(
            user=post.author,
            from_user=request.user,
            notification_type=Notification.Type.LIKE,
            post=post,
        )
    else:
        like.delete()

    return redirect(request.POST.get('next') or 'frontend:home')


@login_required
def comment_post_view(request, post_id):
    post = get_object_or_404(Post.objects.select_related('author'), id=post_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.post = post
        comment.save()
        create_notification(
            user=post.author,
            from_user=request.user,
            notification_type=Notification.Type.COMMENT,
            post=post,
        )

    return redirect(request.POST.get('next') or 'frontend:home')


@login_required
def delete_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user == request.user or request.user.is_staff:
        comment.delete()
    return redirect(request.POST.get('next') or 'frontend:home')


def profile_view(request, user_id):
    profile = get_object_or_404(User, id=user_id)
    posts = (
        Post.objects.select_related('author')
        .prefetch_related('comments__user', 'likes')
        .filter(author=profile)
        .annotate(likes_total=Count('likes', distinct=True), comments_total=Count('comments', distinct=True))
        .order_by('-created_at')
    )

    is_owner = request.user.is_authenticated and request.user == profile
    profile_form = ProfileForm(instance=profile) if is_owner else None

    context = {
        'profile': profile,
        'posts': posts,
        'profile_form': profile_form,
        'comment_form': CommentForm(),
        'followers_count': Follow.objects.filter(following=profile).count(),
        'following_count': Follow.objects.filter(follower=profile).count(),
        'is_following': request.user.is_authenticated
        and Follow.objects.filter(follower=request.user, following=profile).exists(),
        **viewer_state(request.user),
    }
    return render(request, 'frontend/profile.html', context)


@login_required
def update_profile_view(request):
    form = ProfileForm(request.POST, request.FILES, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, 'Profile updated.')
    return redirect('frontend:profile', user_id=request.user.id)


@login_required
def follow_user_view(request, user_id):
    target = get_object_or_404(User, id=user_id)
    if target != request.user:
        follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
        if created:
            create_notification(user=target, from_user=request.user, notification_type=Notification.Type.FOLLOW)
        else:
            follow.delete()
    return redirect(request.POST.get('next') or reverse('frontend:profile', args=[user_id]))


@login_required
def notifications_view(request):
    notifications = Notification.objects.select_related('from_user', 'post').filter(user=request.user)
    return render(request, 'frontend/notifications.html', {'notifications': notifications})


@login_required
def mark_notifications_read_view(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('frontend:notifications')


@login_required
def conversations_view(request):
    form = ConversationForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        conversation, _ = get_or_create_direct_conversation(request.user, form.cleaned_data['participant'])
        return redirect('frontend:conversation', conversation_id=conversation.id)

    conversations = (
        Conversation.objects.prefetch_related('participants', 'messages')
        .filter(participants=request.user)
        .order_by('-updated_at')
    )
    return render(request, 'frontend/conversations.html', {'conversations': conversations, 'form': form})


@login_required
def conversation_view(request, conversation_id):
    conversation = get_object_or_404(
        Conversation.objects.prefetch_related('participants').filter(participants=request.user),
        id=conversation_id,
    )

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            conversation.save(update_fields=('updated_at',))
            return redirect('frontend:conversation', conversation_id=conversation.id)
    else:
        form = MessageForm()

    conversation.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)
    messages_qs = conversation.messages.select_related('sender').order_by('created_at')
    token = str(AccessToken.for_user(request.user))

    return render(
        request,
        'frontend/conversation.html',
        {
            'conversation': conversation,
            'conversation_messages': messages_qs,
            'form': form,
            'ws_token': token,
        },
    )


def viewer_state(user):
    if not user.is_authenticated:
        return {'liked_post_ids': set(), 'following_ids': set(), 'unread_notifications_count': 0}

    return {
        'liked_post_ids': set(Like.objects.filter(user=user).values_list('post_id', flat=True)),
        'following_ids': set(Follow.objects.filter(follower=user).values_list('following_id', flat=True)),
        'unread_notifications_count': Notification.objects.filter(user=user, is_read=False).count(),
    }
