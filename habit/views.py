from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetConfirmView, PasswordChangeView
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.http import require_POST

from habits_application import settings
from .forms import HabitForm, CustomLoginForm, CustomUserCreationForm, CustomSetPasswordForm, CustomPasswordChangeForm
from .models import Habit, HabitStatus
from .tokens import account_activation_token

from django.core.cache import cache
from django.http import JsonResponse


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    View for changing user password using a custom form and template.
    After a successful form submission, a success message is displayed and user is redirected to settings page.
    """
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy("settings")
    template_name = "habit/change_password.html"

    def form_valid(self, form):
        messages.success(self.request, "Your password has been successfully changed!")
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    View for confirming password reset using a custom form and template.
    After a successful reset, user is redirected to the login page with a success message.
    """
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy("login")
    template_name = "registration/custom_password_reset_confirm.html"

    def form_valid(self, form):
        messages.success(self.request, "Your password has been successfully changed!")
        return super().form_valid(form)


def cache_test(request):
    """
    A test view to demonstrate caching.
    It stores a value in the cache if not already set, or retrieves it otherwise.
    Returns a JsonResponse with the cached value.
    """
    if settings.USE_REDIS_CACHE:
        data = cache.get("my_key")
        if data is None:
            cache.set("my_key", "Hello via HTTP!", timeout=60)
            data = "SET NEW VALUE"
    else:
        data = "SET NEW VALUE"

    return JsonResponse({"cached_value": data})


@login_required
def habit_list(request):
    """
    Displays the list of habits for the logged-in user.
    The habits are retrieved and rendered using a template.
    """
    habits = Habit.objects.filter(user=request.user).order_by('id')
    return render(request, 'habit/habit_list.html', {'habits': habits})


@login_required
def habit_add(request):
    """
    Adds a new habit for the logged-in user.
    On GET, renders the habit creation form.
    On POST, saves the new habit and redirects to the habit list.
    """
    if request.method == "POST":
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.save()
            messages.success(request, f"Habit '{habit.name}' has been created!")
            return redirect('habit_list')
    else:
        form = HabitForm()
    return render(request, 'habit/habit_add.html', {'form': form})


@login_required
def habit_edit(request, pk):
    """
    Edits an existing habit for the logged-in user.
    Retrieves the habit by primary key, renders the edit form, and saves the updates if valid.
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    if request.method == "POST":
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            habit.save()
            messages.success(request, f"Habit '{habit.name}' has been updated!")
            return redirect('habit_detail', pk=habit.pk)
        else:
            messages.error(request, "Error creating the habit. Please make sure all required fields are filled in!")
    else:
        form = HabitForm(instance=habit)
    return render(request, 'habit/habit_edit.html', {'form': form})


@login_required
def habit_delete(request, pk):
    """
    Deletes a habit for the logged-in user.
    On POST, the habit is deleted and a success message is shown.
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    if request.method == 'POST':
        habit.delete()
        messages.success(request, f"Habit '{habit.name}' has been deleted!")
        return redirect('habit_list')
    return render(request, 'habit/habit_delete_confirm.html', {'habit': habit})


from calendar import monthrange
from datetime import date


@login_required
def habit_detail(request, pk):
    """
    Displays the habit details for a specific month and allows switching between months.
    Retrieves the habit, its statuses for the selected month, and prepares data for rendering the calendar view.
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)

    try:
        month = int(request.GET.get('month', date.today().month))
        year = int(request.GET.get('year', date.today().year))
    except ValueError:
        month = date.today().month
        year = date.today().year

    num_days = monthrange(year, month)[1]
    days = list(range(1, num_days + 1))

    first_weekday = date(year, month, 1).weekday()

    statuses = HabitStatus.objects.filter(
        habit=habit,
        user=request.user,
        date__year=year,
        date__month=month
    )

    status_dict = {s.date.day: s.done for s in statuses}

    def get_prev_next_month(month, year):
        if month == 1:
            prev_month = 12
            prev_year = year - 1
        else:
            prev_month = month - 1
            prev_year = year

        if month == 12:
            next_month = 1
            next_year = year + 1
        else:
            next_month = month + 1
            next_year = year

        return {'month': prev_month, 'year': prev_year}, {'month': next_month, 'year': next_year}

    prev_month, next_month = get_prev_next_month(month, year)

    context = {
        'habit': habit,
        'days': days,
        'first_weekday': first_weekday,
        'status_dict': status_dict,
        'month': month,
        'year': year,
        'month_name': date(year, month, 1).strftime("%B"),
        'today': date.today().day if date.today().month == month and date.today().year == year else -1,
        'prev_month': prev_month,
        'next_month': next_month,
    }

    return render(request, 'habit/habit_detail.html', context)


@login_required
@require_POST
def update_habit_calendar(request, pk):
    """
    Updates or deletes a habit's status for a specific day in any selected month.
    Handles POST requests with day, month, year, and action parameters.
    Redirects to the same calendar view for the selected month.
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)

    day = int(request.POST.get('day'))
    month = int(request.POST.get('month'))
    year = int(request.POST.get('year'))
    action = request.POST.get('action')

    if action not in ['done', 'not_done', 'none']:
        return redirect('habit_calendar', pk=habit.pk)

    try:
        chosen_date = date(year, month, day)
    except ValueError:
        return redirect('habit_calendar', pk=habit.pk)

    if action == 'none':
        HabitStatus.objects.filter(user=request.user, habit=habit, date=chosen_date).delete()
    else:
        status, _ = HabitStatus.objects.get_or_create(
            user=request.user,
            habit=habit,
            date=chosen_date
        )
        status.done = (action == 'done')
        status.save()

    return redirect(f"{reverse('habit_calendar', kwargs={'pk': habit.pk})}?month={month}&year={year}")


@login_required
def more(request):
    """
    Renders a simple 'more' page with an optional form or information.
    """
    return render(request, 'habit/more.html', {})


@login_required
def settings_view(request):
    """
    Renders the settings page for the logged-in user.
    """
    return render(request, 'habit/settings.html')


def login_view(request):
    """
    Custom login view.
    Handles login attempts, authenticates users, and redirects to the habit list on success.
    """
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data['remember_me']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                if remember_me:
                    request.session.set_expiry(3600 * 24 * 30)
                else:
                    request.session.set_expiry(0)

                return redirect('habit_list')
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = CustomLoginForm()

    return render(request, 'registration/login.html', {'form': form})


def register(request):
    """
    Custom user registration view.
    Allows users to register with a form, then sends an email with an activation link.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = "Activate your account"
            message = render_to_string("registration/activation_email.html", {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get("email")
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.content_subtype = "html"
            email.send()
            messages.success(request, "Please check your email to complete the registration")
            return redirect("login")

    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})


def activate(request, uidb64, token):
    """
    Activates a user's account after clicking on the activation link.
    Verifies the token and activates the user's account if valid.
    """
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Your account has been successfully activated!")
        return redirect("login")
    else:
        messages.error(request, "Activation link is invalid or expired.")
        return redirect("login")


def custom_404(request, exception):
    """
    Custom 404 error page.
    """
    return render(request, 'errors/404.html', status=404)


def custom_500(request):
    """
    Custom 500 error page.
    """
    return render(request, 'errors/500.html', status=500)


def custom_403(request, exception):
    """
    Custom 403 error page.
    """
    return render(request, 'errors/403.html', status=403)


def custom_400(request, exception):
    """
    Custom 400 error page.
    """
    return render(request, 'errors/400.html', status=400)
