from django.contrib.auth.models import  User
from django.db import models
from datetime import date, timedelta


class Habit(models.Model):
    """Model representing a user-defined habit.
    Fields:
    - user: Owner of the habit
    - name, description: Basic info
    - color: Used for UI styling
    - duration_days: Optional fixed length (used if not unlimited)
    - is_unlimited: If True, habit has no time limit (default=False)
    - created_at, updated_at: Auto-managed timestamps
    Model has 2 methods score and current_streak"""
    FREQUENCY_CHOICES = [
        (1, 'Every Day'),
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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField("Habit Name", max_length=200)
    description = models.TextField("Habit Description (Optional)", blank=True, null=True)
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, default='blue')
    duration_days = models.PositiveIntegerField(null=True, blank=True)
    is_unlimited = models.BooleanField(default=False)
    # hidden auto field
    created_at = models.DateTimeField(auto_now_add=True)
    # hidden auto field
    updated_at = models.DateTimeField(auto_now=True)

    def score(self):
        """ Calculates completion score (percentage) of the habit.
        - Uses duration_days if set, or counts from creation date to today.
        - If no days have passed, returns 0 to avoid division by zero.
        Returns:
       int: Completion score (0–100). """

        start_date = self.created_at.date()
        today = date.today()
        days_active = (today - start_date).days + 1

        # Use duration_days if set and habit is not unlimited
        if self.duration_days and not self.is_unlimited:
            days_active = min(days_active, self.duration_days)

        if days_active == 0:
            return 0

        completed_days = HabitStatus.objects.filter(
            habit=self,
            user=self.user,
            done=True,
            date__lte=today, # less than or equal
            date__gte=start_date # greater or equal
        ).count()

        return round((completed_days / days_active) * 100)

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
        previous_date  = None
        for success_day in success_days:
            if previous_date is None:
                current = 1
            elif success_day.date == previous_date + timedelta(days=1):
                current += 1
            else:
                current = 1

            best = max(best,current)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
