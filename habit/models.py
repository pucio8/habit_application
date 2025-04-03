from django.conf import settings
from django.db import models


"""Model of Habit"""


class Habit(models.Model):
    FREQUENCY_CHOICES = [
        (1, 'Daily'),
        (7, 'Weekly'),
        (30, 'Monthly'),
    ]

    COLOR_CHOICES = [
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('orange', 'Orange'),
        ('purple', 'Purple'),
        ('pink', 'Pink'),
        ('brown', 'Brown'),
        ('gray', 'Gray'),
        ('black', 'Black'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    frequency = models.IntegerField(choices=FREQUENCY_CHOICES, default=1)
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, default='blue')
    duration_days = models.PositiveIntegerField(null=True, blank=True)
    is_unlimited = models.BooleanField(default=False)
    # hidden auto field
    created_at = models.DateTimeField(auto_now_add=True)
    # hidden auto field
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    """Create Habit"""

    @classmethod
    def add_habit(cls, author, name, description=None):
        pass

    """Remove Habit"""

    @classmethod
    def remove_habit(cls, habit_id):
        pass
