from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Habit
from django.core.exceptions import ValidationError


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
    remember_me = forms.BooleanField(required=False, label="Remember me")

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with those email adress already exists!")
        return email