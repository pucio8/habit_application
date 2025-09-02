from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    A custom user model that inherits from Django's AbstractUser.

    This model makes the `email` field required and unique for each user,
    but otherwise retains all the standard fields and behaviors of the
    default Django user model.
    """
    # Override the default email field to make it unique and required for registration.
    email = models.EmailField(
        max_length=100,
        unique=True,
        help_text="Required. A unique email address is needed."
    )

    # We do not set USERNAME_FIELD = "email" here.
    # Instead, we rely on our custom authentication backend (`EmailOrUsernameBackend`)
    # to handle logging in with either the username or the email address.
    # This keeps the model's behavior closer to Django's default.