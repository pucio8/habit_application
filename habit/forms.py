from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, SetPasswordForm, PasswordChangeForm
from .models import Habit
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ('name', 'description', 'color')
        widgets = {
            'name': forms.TextInput(attrs={'id': 'name-field', 'class': 'form-input'}),
            'description': forms.TextInput(attrs={'id': 'description-field', 'class': 'form-input'}),
            'color': forms.Select(attrs={'id': 'color-field', 'class': 'form-input'}),
        }


class CustomLoginForm(AuthenticationForm):
    """Custom login form with optional 'Remember me' checkbox."""
    remember_me = forms.BooleanField(required=False, label="Remember me")


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form with required and unique email."""
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with those email adress already exists!")
        return email


class CustomSetPasswordForm(SetPasswordForm):
    """Custom form for setting a new password"""

    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "New Password"}),
        label="New Password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Repeat New Password"}),
        label="Password confirmation"
    )

class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with current and new password fields."""
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Current password"}),
        label="Current password"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "New password"}),
        label="New password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New password'}),
        label="New password"
    )
