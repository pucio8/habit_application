from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

class EmailOrUsernameBackend(ModelBackend):
    """
    An authentication backend that allows users to log in using either their
    username or email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Overrides the default authenticate method to allow login with email or username.
        It finds the user by either field, then validates the password and active status.
        """
        UserModel = get_user_model()
        
        try:
            # Find a user matching either the username or the email (case-insensitive).
            user = UserModel.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except UserModel.DoesNotExist:
            return None

        # Check the password and if the user is permitted to authenticate.
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None