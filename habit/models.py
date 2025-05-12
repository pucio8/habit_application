from django.db import models
from datetime import date, timedelta

from users.models import CustomUser


class Habit(models.Model):
    """
    Model representing a user-defined habit.

    Fields:
    - user: The owner of the habit (ForeignKey to CustomUser)
    - name: Name of the habit
    - description: Optional description of the habit
    - color: The color associated with the habit for UI styling
    - created_at: Timestamp when the habit was created (auto-managed)
    - updated_at: Timestamp when the habit was last updated (auto-managed)

    Methods:
    - score: Calculates the completion percentage of the habit between the first and last status entries.
    - current_streak: Returns the number of consecutive days the habit has been completed.
    - best_streak: Returns the longest consecutive streak of days the habit has been completed.

    Available colors for habits:
    - Bright Blue (dodgerblue)       #0466c8
    - Tomato (crimson)               #d62828
    - Gold (gold)                    #ffd60a
    - Light Pink (lightpink)         #ffa5ab
    - Olive (olive)                  #606c38
    - Indian Red (peru)              #b17f59
    - Indigo (slateblue)             #415a77
    - Thistle (thistle)              #9c89b8

    Note:
    - Colors are stored as simple names in the database (e.g., 'dodgerblue', 'crimson').
    - Hex codes are provided for visual reference.
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
        Missing entries (no status) are treated as not done (0%).

        Returns:
        int: Completion percentage of the habit.
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
        """Returns the number of consecutive days the habit has been completed (streak).
            The streak is counted starting from the current day and moving backwards.

            Returns:
                int: The number of consecutive days the habit was completed.
                """
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
        """Returns the longest streak (consecutive days) the habit was completed.

            Returns:
            int: The longest streak of consecutive days the habit was completed.
            """
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
    """ Tracks daily completion of a habit.
    Each entry represents whether a user completed a specific habit on a given day.

    Constraints:
    - One entry per user, habit, and day (unique constraint).

    Fields:
    - user: The user who completed the habit
    - habit: The habit that was completed
    - date: The date for which the habit was completed
    - done: Whether the habit was completed on the given day (True/False)

    Meta:
    - Ensures that a user can only have one entry per habit per day.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    habit = models.ForeignKey('Habit', on_delete=models.CASCADE)
    date = models.DateField()  # day to which the logic applies
    done = models.BooleanField(null=True, default=None)

    class Meta:
        """Returns a string representation of the HabitStatus instance.
            It shows the user's name, the habit name, the date, and whether the habit was completed (✔️/❌).

        Returns:
        str: A formatted string showing the habit status.
        """
        unique_together = ('user', 'habit', 'date')  # does not allow to save duplicate for the same day

    def __str__(self):
        status = "✔️" if self.done else "❌"
        return f"{self.user.username} – {self.habit.name} on {self.date}: {status}"
