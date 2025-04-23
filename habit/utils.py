from .models import Habit, HabitStatus
from datetime import date

def create_habit_status_for_all_users():
    today = date.today()

    for habit in Habit.objects.all():
        HabitStatus.objects.get_or_create(
            user=habit.user,
            habit=habit,
            date=today
        )