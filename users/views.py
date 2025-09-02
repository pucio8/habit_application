# Django Imports
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db.models import Q
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.safestring import mark_safe

# Local Imports
from .forms import (
    CustomUserCreationForm,
    CustomLoginForm,
    CustomPasswordChangeForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    ResendActivationEmailForm,
)
from .tokens import account_activation_token

User = get_user_model()


# ==============================================================================
# Class-Based Views for Password Management
# ==============================================================================


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    Handles password changes for logged-in users, using a custom form and
    adding a success message upon completion.
    """
    form_class = CustomPasswordChangeForm
    template_name = "users/registration/password_change.html"
    success_url = reverse_lazy("habit_list")

    def form_valid(self, form):
        """Adds a success message before the parent class handles the redirect."""
        messages.success(self.request, "Your password has been successfully changed!")
        return super().form_valid(form)


class CustomPasswordResetView(PasswordResetView):
    """
    Handles the initial request for a password reset, using a custom
    form and email templates for a consistent user experience.
    """
    form_class = CustomPasswordResetForm
    template_name = "users/registration/password_reset_form.html"
    email_template_name = "users/registration/password_reset_email.html"
    subject_template_name = "users/registration/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Handles the final step of the password reset process where the user
    enters their new password after clicking the link from the email.
    """
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy("login")
    template_name = "users/registration/custom_password_reset_confirm.html"

    def form_valid(self, form):
        """Adds a success message after the password has been successfully set."""
        messages.success(
            self.request, "Your password has been changed successfully! You can now log in."
        )
        return super().form_valid(form)


# ==============================================================================
# Function-Based Views for Core Account Actions
# ==============================================================================


@login_required
def account(request):
    """Renders the main user account page."""
    return render(request, "users/account.html")


def login_view(request):
    """
    Handles user login with correct priority for checks:
    1. User existence & password correctness.
    2. Active status.
    Provides specific feedback for inactive accounts with a link to resend activation.
    """
    if request.user.is_authenticated:
        return redirect("habit_list")

    form = CustomLoginForm()

    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        username_or_email = request.POST.get("username")
        password = request.POST.get("password")

        # Step 1: Find the user in the database first.
        try:
            user = User.objects.get(
                Q(username__iexact=username_or_email) | Q(email__iexact=username_or_email)
            )
        except User.DoesNotExist:
            user = None

        # Step 2: Check if the user exists AND if the password is correct.
        if user is not None and user.check_password(password):
            # Step 3: Only after confirming identity, check the account status.
            if user.is_active:
                # SUCCESS: User exists, password is correct, and account is active.
                # Use authenticate() to get the user object with the correct backend attached.
                user_for_login = authenticate(
                    request, username=username_or_email, password=password
                )
                if user_for_login is not None:
                    login(request, user_for_login)
                    return redirect("habit_list")
            else:
                # INACTIVE ACCOUNT: Password is correct, but the account is not active.
                # Provide a helpful message with a link to resend the activation email.
                resend_url = reverse("resend_activation")
                message_text = f'This account is not active. <a href="{resend_url}" class="alert-link">Click here to resend the activation email.</a>'
                messages.warning(request, mark_safe(message_text), extra_tags="long-timeout")
        else:
            # INVALID CREDENTIALS: User does not exist OR password is incorrect.
            # In both cases, show the same generic error message for security.
            messages.error(request, "Invalid username or password.")

    return render(request, "users/registration/login.html", {"form": form})


def register(request):
    """
    Handles new user registration, creating them as inactive and sending an
    account activation email.
    """
    if request.user.is_authenticated:
        return redirect("habit_list")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Let the form save the user with a password.
            # The user's is_active flag is True by default from the AbstractUser model.
            user = form.save()

            # Now, explicitly set the user to inactive and save only this change.
            user.is_active = False
            user.save(update_fields=["is_active"])

            # Prepare and send the activation email.
            current_site = get_current_site(request)
            mail_subject = "Activate your account"
            message = render_to_string(
                "users/registration/activation_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            email_message = EmailMessage(
                mail_subject, message, to=[form.cleaned_data.get("email")]
            )
            email_message.content_subtype = "html"
            email_message.send()

            messages.success(
                request, "Please check your email to complete the registration."
            )
            return redirect("login")
    else:
        form = CustomUserCreationForm()

    return render(request, "users/registration/register.html", {"form": form})


def activate(request, uidb64, token):
    """
    Activates a user's account after they click the activation link.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        # Activation successful: activate user, log them in, and redirect.
        user.is_active = True
        user.save()
        # Manually attach the backend to the user object before logging in.
        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user)
        messages.success(request, "Your account has been successfully activated!")
        return redirect("habit_list")
    else:
        # Activation failed: show an error message.
        messages.info(request, "Activation link is invalid or expired.")
        return redirect("login")


def resend_activation_email(request):
    """
    Handles the request to resend an activation email for an inactive account.
    """
    if request.user.is_authenticated:
        return redirect("habit_list")

    if request.method == "POST":
        form = ResendActivationEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                # Find the user who has the given email and is inactive.
                user = User.objects.get(email__iexact=email, is_active=False)

                # Explicitly ensure the user remains inactive.
                if user.is_active is not False:
                    user.is_active = False
                    user.save(update_fields=["is_active"])

                # Send the activation email (reusing logic from the register view).
                current_site = get_current_site(request)
                mail_subject = "Activate your account [New Link]"
                message = render_to_string(
                    "users/registration/activation_email.html",
                    {
                        "user": user,
                        "domain": current_site.domain,
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": account_activation_token.make_token(user),
                    },
                )
                email_message = EmailMessage(mail_subject, message, to=[email])
                email_message.content_subtype = "html"
                email_message.send()

            except User.DoesNotExist:
                # If no inactive user is found, do nothing. This prevents leaking
                # information about which email addresses are registered.
                pass

            messages.success(
                request,
                "If an account with that email needs activation, a new link has been sent.",
            )
            return redirect("login")
    else:
        form = ResendActivationEmailForm()

    return render(request, "users/registration/resend_activation_form.html", {"form": form})