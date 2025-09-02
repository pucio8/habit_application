from django import forms
from .models import Habit

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ('name', 'description', 'color')

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ('name', 'description', 'color','start_date')
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g., Drink 8 glasses of water'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'A short description of your habit'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }