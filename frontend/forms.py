from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

from chat.models import Conversation, Message
from posts.models import Post
from social.models import Comment


User = get_user_model()


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    password_confirm = forms.CharField(widget=forms.PasswordInput, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('password_confirm'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = User(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
        )
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'bio', 'avatar')


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('content', 'image')
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What is happening?'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.TextInput(attrs={'placeholder': 'Write a comment...'}),
        }


class ConversationForm(forms.Form):
    participant = forms.ModelChoiceField(queryset=User.objects.none())

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['participant'].queryset = User.objects.exclude(id=user.id).order_by('username')


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('content',)
        widgets = {
            'content': forms.TextInput(attrs={'placeholder': 'Message...'}),
        }
