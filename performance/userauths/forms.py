from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Username"}),
        error_messages={
            'required': "Username is required.",
            'invalid': "Invalid username."
        }
    )
    email = forms.CharField(
        widget=forms.EmailInput(attrs={"placeholder": "Email"}),
        error_messages={
            'required': "Email is required.",
            'invalid': "Enter a valid email address."
        }
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password"}),
        error_messages={
            'required': "Password is required.",
        }
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm password"}),
        error_messages={
            'required': "Please confirm your password.",
        }
    )

    class Meta:
        model = User
        fields = ['username', 'email']
