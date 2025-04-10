from .models import Habit, HabitStatus
from datetime import date

def create_habit_status_for_all_users():
    today = date.today()

    # for all Habits
    for habit in Habit.objects.all():
        # create HabitStatus() for all
        HabitStatus.objects.get_or_create(
            user=habit.user,
            habit=habit,
            date=today
        )