from django import forms
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Custom_Users, registered_users, journalist_users, article, comment
from django.contrib.auth import get_user_model
from tinymce.widgets import TinyMCE

User = get_user_model()

class UsersSignupForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Email',
            'style': 'padding:6px; font-size: 15px;'
        }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Password',
            'style': 'padding:6px; font-size: 15px;'
        }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'style': 'padding:6px; font-size: 15px;'
        }))
    username = forms.CharField(widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Username',
            'style': 'padding:6px; font-size: 15px;'
        }))
    bio = forms.CharField(widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Bio',
            'style': 'padding:6px; font-size: 15px; '
        }))
    
    class Meta(UserCreationForm.Meta):
        model = Custom_Users
        fields = ('username', 'email', 'password1', 'password2', 'bio')
        
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_registered_user = True
        if commit:
            user.save()
            registered_user = registered_users.objects.create(user=user, bio=self.cleaned_data.get('bio'))
        return user



class JournalistSignupForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Username',
            'style': 'padding:6px; font-size: 15px;'
        }))
    email = forms.EmailField(widget=forms.EmailInput())
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    first_name = forms.CharField(widget=forms.TextInput())
    last_name = forms.CharField(widget=forms.TextInput())
    bio = forms.CharField(widget=forms.TextInput())
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_journalist_user = True
        if commit:
            user.save()
        journalist_user = journalist_users.objects.create(user=user, first_name=self.cleaned_data.get('first_name'),last_name=self.cleaned_data.get('last_name'))
        return user




class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())

class ArticleForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={'id': 'custom_id_for_content', 'class':'contentform'}))

    class Meta:
        model = article
        fields = ('title','slug','image','content', 'tags')


class CommentForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'md-textarea form-control',
        'placeholder': 'comment here ...',
        'rows': '4', 'id': 'id_body'
    }))
    class Meta:
        model = comment
        fields = ['body']