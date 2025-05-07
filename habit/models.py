from django.contrib.auth.models import User
from django.db import models
from datetime import date, timedelta

from users.models import CustomUser


class Habit(models.Model):
    """
    Model representing a user-defined habit.

    Fields:
    - user: Owner of the habit
    - name, description: Basic info
    - color: Used for UI styling
    - created_at, updated_at: Auto-managed timestamps

    Model has 2 methods: score and current_streak.

    Available colors for habits.

    Note:
    - In the database, colors are stored as simple names (e.g., 'brightblue', 'olive', 'gold').
    - The hex codes below are only for visual reference:

        #0466c8  (Bright Blue)
        #606c38  (Olive)
        #415a77  (Slate Blue)
        #d62828  (Crimson)
        #ffd60a  (Gold)
        #9c89b8  (Thistle)
        #ffa5ab  (Light Pink)
        #b17f59  (Peru)
    """

    COLOR_CHOICES = [
        ('dodgerblue', 'Bright Blue'),
        ('crimson', 'Tomato'),
        ('gold', 'Gold'),
        ('lightpink', 'Light Pink'),
        ('olive', 'Olive'),
        ('peru', 'Indian Red '),
        ('slateblue', 'Indigo'),
        ('thistle', 'Thistle'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField("Habit Name", max_length=200)
    description = models.CharField("Habit Description (Optional)", blank=True, null=True, max_length=200)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='blue')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def score(self):
        """
        Calculates habit completion score between the first and last status entries.
        Missing entries are treated as not done.
        """
        statuses = HabitStatus.objects.filter(habit=self, user=self.user)
        if not statuses.exists():
            return 0

        start_date = statuses.order_by('date').first().date
        end_date = statuses.order_by('-date').first().date

        total_days = (end_date - start_date).days + 1
        status_dict = {s.date: s.done for s in statuses}

        completed_days = sum(1 for i in range(total_days)
                             if status_dict.get(start_date + timedelta(days=i)) is True)

        return round((completed_days / total_days) * 100)

    def current_streak(self):
        """Returns the number of consecutive days the habit has been completed (streak)."""
        check_date = date.today()
        streak = 0

        while True:
            try:
                status = HabitStatus.objects.get(
                    habit=self,
                    user=self.user,
                    date=check_date
                )
                if status.done:
                    streak += 1
                else:
                    break
            except HabitStatus.DoesNotExist:
                break

            check_date -= timedelta(days=1)

        return streak

    def best_streak(self):
        """Returns the longest streak (consecutive days) the habit was completed."""
        success_days = HabitStatus.objects.filter(
            habit=self,
            user=self.user,
            done=True
        ).order_by('date')

        best = 0
        current = 0
        previous_date = None
        for success_day in success_days:
            if previous_date is None:
                current = 1
            elif success_day.date == previous_date + timedelta(days=1):
                current += 1
            else:
                current = 1

            best = max(best, current)
            previous_date = success_day.date

        return best

    def __str__(self):
        return self.name


class HabitStatus(models.Model):
    """Tracks daily completion of a habit.
    Each entry represents whether a user completed a specific habit on a given day.
    Constraints:
    - One entry per user, habit, and day
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    habit = models.ForeignKey('Habit', on_delete=models.CASCADE)
    date = models.DateField()  # day to which the logic applies
    done = models.BooleanField(null=True, default=None)

    class Meta:
        """Ensures a user can only have one logical per habit per day.
        Prevents duplicate entries for the same habit on the same date."""
        unique_together = ('user', 'habit', 'date')  # does not allow to save duplicate for the same day

    def __str__(self):
        status = "✔️" if self.done else "❌"
        return f"{self.user.username} – {self.habit.name} on {self.date}: {status}"
