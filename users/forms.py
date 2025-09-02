# in users/forms.py

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm, SetPasswordForm,
    PasswordChangeForm, PasswordResetForm
)
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags


User = get_user_model()


# ==============================================================================
# Base Form for Consistent Styling
# ==============================================================================

class BaseUserForm(forms.Form):
    """
    A base form to apply common customizations to all user-related forms.
    It removes the default colon (':') suffix from all field labels.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Removes the colon from all forms that inherit from this class.
        self.label_suffix = ""


# ==============================================================================
# Custom Authentication Forms
# ==============================================================================

class CustomLoginForm(BaseUserForm, AuthenticationForm):
    """A custom login form that uses the underlined input style."""
    username = forms.CharField(
        label='Username or Email',
        widget=forms.TextInput(attrs={
            'class': 'form-control-underline',
            'placeholder': 'Type your username or email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control-underline',
            'placeholder': 'Type your password'
        })
    )


class CustomUserCreationForm(BaseUserForm, UserCreationForm):
    """A custom registration form that applies the underlined style and adds tooltips."""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        placeholders = {
            'username': 'Choose a unique username',
            'email': 'Enter your email address',
            'password1': 'Create a strong password',
            'password2': 'Repeat the password',
        }
        
        for field_name, field in self.fields.items():
            # Apply the custom underlined style to all fields.
            field.widget.attrs.update({'class': 'form-control-underline'})
            
            # Add placeholders where defined.
            if field_name in placeholders:
                field.widget.attrs.update({'placeholder': placeholders[field_name]})
            
            # Convert Django's help text into a Bootstrap tooltip for a cleaner UI.
            if field.help_text:
                clean_help_text = strip_tags(field.help_text)
                field.widget.attrs['title'] = clean_help_text
                field.widget.attrs['data-bs-toggle'] = 'tooltip'
                field.help_text = ''  # Clear the original help text.

    def clean_email(self):
        """Ensures that the email address is not already in use."""
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email


class CustomPasswordResetForm(BaseUserForm, PasswordResetForm):
    """A custom password reset form with the underlined style."""
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control-underline',
            'placeholder': 'Enter your email to reset password',
            'autofocus': True
        })
    )


class CustomSetPasswordForm(SetPasswordForm):
    """
    A custom password set form that applies custom styling to its fields.
    Inherits from Django's default SetPasswordForm.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control-underline',
            'placeholder': 'Enter a new password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control-underline',
            'placeholder': 'Repeat the new password'
        })


class CustomPasswordChangeForm(PasswordChangeForm):
    """A custom password change form that applies custom styling."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control-underline',
            'placeholder': 'Current password'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control-underline',
            'placeholder': 'New password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control-underline',
            'placeholder': 'New password confirmation'
        })

# --- Correction is here ---
class ResendActivationEmailForm(BaseUserForm, forms.Form):
    """A form for users to request a new activation email."""
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control-underline',
            'placeholder': 'Enter your registered email address',
            'autofocus': True
        })
    )
    # The __init__ method is no longer needed here, because this form
    # now inherits the label_suffix = "" behavior from BaseUserForm.