# in users/tests.py

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# Get the custom user model defined for the project.
User = get_user_model()


class UserViewsTest(TestCase):
    """
    Test suite for the views within the 'users' application.
    
    This class contains tests to ensure that the user-related pages and logic
    (like login, registration, etc.) are functioning correctly.
    """

    def setUp(self):
        """
        Set up a non-active user and test data for all tests in this class.
        This method is run automatically before each test function.
        """
        self.username = "testuser"
        self.email = "test@example.com"
        self.password = "strong-password-123"

        # Create a user but keep them inactive, simulating the state right after registration.
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
            is_active=False,
        )

    def test_login_page_loads_correctly(self):
        """
        Tests that the login page can be accessed via a GET request and returns a
        successful HTTP 200 OK response.
        """
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login_page_uses_correct_template(self):
        """
        Tests that the login page view renders using the correct HTML template.
        """
        response = self.client.get(reverse("login"))
        self.assertTemplateUsed(response, "users/registration/login.html")

    def test_inactive_user_cannot_login(self):
        """
        Tests that a user with is_active=False cannot log in and sees the
        correct warning message. This is a crucial regression test.
        """
        # Simulate the inactive user submitting the login form with correct credentials.
        response = self.client.post(
            reverse("login"), {"username": self.email, "password": self.password}
        )

        # Assert that the login failed and the page was re-rendered (no redirect).
        self.assertEqual(response.status_code, 200)

        # Assert that the specific "account not active" message was passed to the template.
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn("This account is not active", str(messages[0]))

    def test_active_user_can_login_successfully(self):
        """
        Tests that a user with is_active=True can log in successfully and is
        redirected to the habit list page.
        """
        # For this test, we need an active user.
        self.user.is_active = True
        self.user.save()

        # Simulate the active user submitting the login form with correct credentials.
        response = self.client.post(
            reverse("login"), {"username": self.email, "password": self.password}
        )

        # Assert that the login was successful and the user was redirected.
        self.assertRedirects(response, reverse("habit_list"))