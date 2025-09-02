from django.db import models
from datetime import date, timedelta
from django.utils import timezone

from users.models import CustomUser


class Habit(models.Model):
    """
    Model representing a user-defined habit.

    Fields:
    - user: The owner of the habit (ForeignKey to CustomUser).
    - name: Name of the habit.
    - description: Optional description of the habit.
    - color: The color associated with the habit for UI styling.
    - start_date: The date when the habit tracking begins.
    - created_at: Timestamp when the habit was created (auto-managed).
    - updated_at: Timestamp when the habit was last updated (auto-managed).

    Methods:
    - score: Calculates the completion percentage of the habit over the last 30 days.
    - current_streak: Returns the number of consecutive days the habit has been completed up to today or yesterday.
    - best_streak: Returns the longest consecutive streak of days the habit has ever been completed.

    Available colors for habits:
    - Blue:      #0d6efd
    - Indigo:    #6f42c1
    - Pink:      #d63384
    - Red:       #dc3545
    - Orange:    #fd7e14
    - Yellow:    #ffc107
    - Green:     #198754
    - Teal:      #0dcaf0
    - Gray:      #6c757d
    """

    COLOR_CHOICES = [
        ("#0d6efd", "Blue"),
        ("#6f42c1", "Indigo"),
        ("#d63384", "Pink"),
        ("#dc3545", "Red"),
        ("#fd7e14", "Orange"),
        ("#ffc107", "Yellow"),
        ("#198754", "Green"),
        ("#0dcaf0", "Teal"),
        ("#6c757d", "Gray"),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField("Habit Name", max_length=200)
    description = models.CharField(
        "Habit Description (Optional)", blank=True, null=True, max_length=200
    )
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default="#0d6efd")
    start_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def score(self):
        """
        Calculates the habit's completion score as a percentage.

        The score is calculated for a 30-day window ending today, but does not
        consider any days before the habit's official `start_date`.
        """
        today = date.today()
        start_period = today - timedelta(days=29)

        # The calculation period should not start before the habit's defined start date.
        if start_period < self.start_date:
            start_period = self.start_date

        # Ensure the calculation does not include future days.
        end_period = today
        if self.start_date > today:
            return 0  # If the habit is set to start in the future, its score is 0.

        total_days_in_period = (end_period - start_period).days + 1
        if total_days_in_period <= 0:
            return 0

        statuses = HabitStatus.objects.filter(
            habit=self, user=self.user, date__range=[start_period, end_period]
        )
        completed_days = statuses.filter(done=True).count()

        return round((completed_days / total_days_in_period) * 100)

    def current_streak(self):
        """
        Calculates the current, unbroken streak of completed days for the habit.
        
        A streak is considered 'current' if the last completed day was either
        today or yesterday. This allows for flexibility, e.g., completing a
        habit late at night and marking it the next morning.
        """
        today = date.today()
        # A streak cannot exist before the habit's start_date.
        if today < self.start_date:
            return 0

        statuses = HabitStatus.objects.filter(
            habit=self, user=self.user, date__lte=today, done=True
        ).order_by('-date')

        if not statuses.exists():
            return 0

        # If the last completion was before yesterday, the current streak is broken.
        if statuses.first().date not in [today, today - timedelta(days=1)]:
            return 0
            
        streak = 0
        # Start checking for consecutive days from today backwards.
        expected_date = today

        for status in statuses:
            if status.date == expected_date:
                streak += 1
                expected_date -= timedelta(days=1)
            else:
                # If there is a gap in dates, the streak is broken.
                break
        
        return streak

    def best_streak(self):
        """
        Calculates the longest unbroken streak of completed days for the habit
        throughout its entire history.
        """
        # Only consider statuses from the habit's start_date onwards.
        statuses = HabitStatus.objects.filter(
            habit=self, user=self.user, done=True, date__gte=self.start_date
        ).order_by('date')
        
        if not statuses.exists():
            return 0

        best_streak = 0
        current_streak = 0
        last_date = None

        for status in statuses:
            # Check if the current status is for the day after the last one.
            if last_date and status.date == last_date + timedelta(days=1):
                current_streak += 1
            else:
                # If not consecutive, reset and start a new streak count.
                current_streak = 1
            
            if current_streak > best_streak:
                best_streak = current_streak
            
            last_date = status.date
            
        return best_streak


class HabitStatus(models.Model):
    """
    Tracks the daily completion status of a habit.

    Each entry represents whether a user completed a specific habit on a given day.

    Fields:
    - user: The user associated with this status entry.
    - habit: The habit this status entry refers to.
    - date: The specific date for this status entry.
    - done: Boolean indicating completion (True=done, False=not done, Null=unmarked).
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    habit = models.ForeignKey("Habit", on_delete=models.CASCADE, related_name="statuses")
    date = models.DateField()
    done = models.BooleanField(
        null=True,
        default=None,
        help_text="Tracks completion: True for done, False for not done, Null if not yet marked.",
    )

    class Meta:
        # Ensures a user can only have one status entry per habit per day.
        unique_together = (
            "user",
            "habit",
            "date",
        )

    def __str__(self):
        """
        Returns a string representation of the HabitStatus instance.

        Example: "username – Habit Name on 2023-10-27: ✔️"

        Returns:
            str: A formatted string showing the user, habit, date, and completion status.
        """
        status_icon = "✔️" if self.done else "❌" if self.done is False else "➖"
        return f"{self.user.username} – {self.habit.name} on {self.date}: {status_icon}"