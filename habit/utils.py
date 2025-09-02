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

def get_prev_next_month(month, year):
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year
    return {'month': prev_month, 'year': prev_year}, {'month': next_month, 'year': next_year}