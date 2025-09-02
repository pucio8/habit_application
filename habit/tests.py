# in habit/tests.py

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from .models import Habit, HabitStatus

User = get_user_model()


class HabitModelTests(TestCase):
    """
    Test suite for the Habit and HabitStatus models.
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='password123'
        )
        self.habit = Habit.objects.create(
            user=self.user,
            name='Test Reading Habit',
            start_date=timezone.now().date() - timedelta(days=30),
        )

    def test_best_streak_calculation(self):
        today = timezone.now().date()
        HabitStatus.objects.create(habit=self.habit, user=self.user, date=today - timedelta(days=5), done=True)
        HabitStatus.objects.create(habit=self.habit, user=self.user, date=today - timedelta(days=4), done=True)
        HabitStatus.objects.create(habit=self.habit, user=self.user, date=today - timedelta(days=3), done=True)
        streak = self.habit.best_streak()
        self.assertEqual(streak, 3)

    def test_current_streak_calculation(self):
        today = timezone.now().date()
        HabitStatus.objects.create(habit=self.habit, user=self.user, date=today - timedelta(days=10), done=True)
        HabitStatus.objects.create(habit=self.habit, user=self.user, date=today - timedelta(days=9), done=True)
        HabitStatus.objects.create(habit=self.habit, user=self.user, date=today - timedelta(days=1), done=True)
        HabitStatus.objects.create(habit=self.habit, user=self.user, date=today, done=True)
        streak = self.habit.current_streak()
        self.assertEqual(streak, 2)

    def test_score_calculation_is_correct(self):
        """
        Tests that the score method correctly calculates the completion
        percentage over the relevant period (last 30 days from today).
        """
        # Arrange: Create a predictable history. We will create exactly 9 'done'
        # statuses within the last 30 days for an expected score of 30%.
        today = timezone.now().date()
        
        # To ensure this test is isolated, let's clear any statuses
        # that might exist for this habit from other tests.
        HabitStatus.objects.filter(habit=self.habit).delete()

        for i in range(30):
            # We create 9 statuses marked as 'done' and the rest as 'not done'.
            if i < 9:
                is_done = True
            else:
                is_done = False
            
            HabitStatus.objects.create(
                habit=self.habit,
                user=self.user,
                date=today - timedelta(days=i),
                done=is_done
            )

        # Act: Call the method we want to test.
        calculated_score = self.habit.score()

        # Assert: 9 completed days out of a 30-day period should be 30%.
        # The score method returns a rounded integer.
        self.assertEqual(calculated_score, 30)


class HabitViewsTest(TestCase):
    """
    Test suite for the views of the 'habit' application.
    """
    def setUp(self):
        """
        Create two different users to test data isolation.
        """
        self.user_a = User.objects.create_user(
            username='user_a',
            email='user_a@example.com', # <-- POPRAWKA: Dodany unikalny email
            password='password123'
        )
        self.user_b = User.objects.create_user(
            username='user_b',
            email='user_b@example.com', # <-- POPRAWKA: Dodany unikalny email
            password='password123'
        )

    def test_habit_list_redirects_for_anonymous_user(self):
        """
        Tests that an unauthenticated user is redirected to the login page.
        """
        habit_list_url = reverse('habit_list')
        response = self.client.get(habit_list_url)
        login_url = reverse('login')
        expected_redirect_url = f'{login_url}?next={habit_list_url}'
        self.assertRedirects(response, expected_redirect_url)

    def test_user_cannot_access_other_users_habit_detail(self):
        """
        Tests that a user gets a 404 error when trying to access another user's data.
        """
        # Arrange: Create a habit that belongs to user_b.
        secret_habit = Habit.objects.create(
            user=self.user_b,
            name="User B's Secret Habit"
        )
        secret_url = reverse('habit_detail', args=[secret_habit.pk])

        # Act: Log in as user_a and try to access the secret URL.
        self.client.login(username='user_a', password='password123')
        response = self.client.get(secret_url)

        # Assert: Check that the server responded with a 404 Not Found status code.
        self.assertEqual(response.status_code, 404)

    def test_logged_in_user_can_create_habit(self):
        """
        Tests that a logged-in user can successfully create a new habit via a POST request.
        """
        # Arrange: Log in our test user 'user_a'.
        self.client.login(username='user_a', password='password123')
        
        # Define the data for the new habit we want to create.
        form_data = {
            'name': 'New Test Habit',
            'description': 'A description for the test.',
            'color': '#dc3545', # Red
            'start_date': timezone.now().date(),
        }

        # Act: Simulate a POST request to the habit_add URL with the form data.
        add_url = reverse('habit_add')
        response = self.client.post(add_url, data=form_data)

        # Assert: Check the results.
        # 1. Was the user redirected to the habit list page?
        self.assertRedirects(response, reverse('habit_list'))

        # 2. Was exactly one habit created in the database?
        self.assertEqual(Habit.objects.count(), 1)

        # 3. Does the created habit have the correct name?
        created_habit = Habit.objects.first()
        self.assertEqual(created_habit.name, 'New Test Habit')
        self.assertEqual(created_habit.user, self.user_a) # Check ownership
