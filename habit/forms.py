from django import forms

from .models import Habit


class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ('name', 'description', 'color', 'duration_days', 'is_unlimited')
        widgets = {
            'name': forms.TextInput(attrs={'id': 'name-field', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'id': 'description-field', 'class': 'form-input'}),
            'color': forms.Select(attrs={'id': 'color-field', 'class': 'form-input'}),
            'duration_days': forms.NumberInput(attrs={'id': 'duration-field', 'class': 'form-input'}),
            'is_unlimited': forms.CheckboxInput(attrs={'id': 'unlimited-checkbox'}),
        }
