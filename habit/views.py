from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.cache import cache
from habit_application import settings
from . import utils

from .forms import HabitForm
from .models import Habit, HabitStatus

from calendar import Calendar
from datetime import date
import json


def cache_test(request):
    """
    A test view to demonstrate caching functionality with Redis.
    
    If caching is enabled, it stores a value in the cache if not already set,
    or retrieves it otherwise. Returns a JsonResponse with the cached value.
    """
    data = "Redis cache is not enabled."
    if settings.USE_REDIS_CACHE:
        data = cache.get("my_key")
        if data is None:
            # Set a value in the cache with a 60-second timeout.
            cache.set("my_key", "Hello from Redis cache!", timeout=60)
            data = "Value was not in cache. SETTING a new one."
    
    return JsonResponse({"cached_value": data})


@login_required
def habit_list(request):
    """
    Displays the list of all habits for the currently logged-in user.
    """
    habits = Habit.objects.filter(user=request.user).order_by('id')
    # Use a prefixed template path for better organization within the app.
    return render(request, 'habit/habit_list.html', {'habits': habits})


@login_required
def habit_add(request):
    """
    Handles the creation of a new habit.
    
    - On GET: Renders an empty form for creating a habit.
    - On POST: Validates the submitted form data. If valid, creates a new
      habit associated with the logged-in user and redirects to the habit list.
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
    Handles editing an existing habit.
    
    Retrieves the habit by its primary key (pk), ensuring it belongs to the
    logged-in user.
    - On GET: Renders the form pre-filled with the habit's data.
    - On POST: Validates and saves the updated data.
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    if request.method == "POST":
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            form.save()
            messages.success(request, f"Habit '{habit.name}' has been updated!")
            return redirect('habit_detail', pk=habit.pk)
        else:
            messages.error(request, "Error updating the habit. Please check the form for errors.")
    else:
        form = HabitForm(instance=habit)
    # Use a prefixed template path for better organization.
    return render(request, 'habit/habit_edit.html', {'form': form, 'habit': habit})


@login_required
def habit_delete(request, pk):
    """
    Handles the deletion of a specific habit.
    
    - On GET: Displays a confirmation page before deleting.
    - On POST: Deletes the habit and redirects to the habit list.
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    if request.method == 'POST':
        habit_name = habit.name
        habit.delete()
        messages.success(request, f"Habit '{habit_name}' has been deleted!")
        return redirect('habit_list')
    return render(request, 'habit/habit_delete_confirm.html', {'habit': habit})


@login_required
def more(request):
    """
    Renders a simple 'more' page.
    """
    return render(request, 'habit/more.html', {})


@login_required
def habit_detail(request, pk):
    """
    Displays the detailed view of a habit, including a monthly calendar.

    This view generates a calendar for a given month and year (or the current
    month by default) and populates it with the habit's completion status for each day.
    Days before the habit's start date are marked as 'disabled'.
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    today = date.today()
    
    try:
        # Get year and month from GET parameters, defaulting to the current date.
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
    except (ValueError, TypeError):
        year, month = today.year, today.month
    
    current_date_obj = date(year, month, 1)
    
    # Fetch all habit statuses for the given month and year.
    statuses = HabitStatus.objects.filter(habit=habit, date__year=year, date__month=month)
    # Create a quick-access dictionary: {day_number: status (True/False)}
    base_status_dict = {s.date.day: s.done for s in statuses}

    # --- Calendar Generation Logic ---
    # Create a more detailed dictionary that accounts for disabled days.
    detailed_status_dict = {}
    habit_start_date = habit.start_date
    cal = Calendar()

    for day in cal.itermonthdays(year, month):
        if day == 0:
            # itermonthdays returns 0 for days outside the current month.
            continue
        
        current_day_in_loop = date(year, month, day)

        # 1. Check if the calendar day is before the habit's start date.
        if current_day_in_loop < habit_start_date:
            detailed_status_dict[day] = 'disabled'
        else:
            # 2. If the day is valid, get its status (True, False, or None if not set).
            detailed_status_dict[day] = base_status_dict.get(day, None)
            
    prev_month, next_month = utils.get_prev_next_month(month, year)

    context = {
        'habit': habit,
        'days': [d for d in cal.itermonthdays(year, month) if d != 0],
        'first_weekday': current_date_obj.weekday(),
        'status_dict': detailed_status_dict,  # Pass the enhanced status dictionary.
        'month': month,
        'year': year,
        'month_name': current_date_obj.strftime("%B"),
        'today': today.day if today.month == month and today.year == year else -1,
        'prev_month': prev_month,
        'next_month': next_month,
    }
    
    return render(request, 'habit/habit_detail.html', context)


@login_required
@require_POST
def update_habit_calendar(request, pk):
    """
    Handles AJAX requests to update a habit's status for a specific day.

    It expects a JSON payload with 'day', 'month', 'year', and 'action'.
    The 'action' determines the new state: 'done', 'not-done', or 'none' (unmarked).
    
    Returns a JSON response with the operation status, the new state of the day,
    and the updated habit statistics (streaks, score).
    """
    try:
        data = json.loads(request.body)
        habit = get_object_or_404(Habit, pk=pk, user=request.user)
        
        day = int(data.get('day'))
        month = int(data.get('month'))
        year = int(data.get('year'))
        action = data.get('action')

        current_date = date(year, month, day)

        # This will be the new state sent back to the frontend.
        new_state_for_js = 'none'

        if action == 'done':
            HabitStatus.objects.update_or_create(
                habit=habit, date=current_date, user=request.user,
                defaults={'done': True}
            )
            new_state_for_js = 'done'
        
        elif action == 'not-done':
            HabitStatus.objects.update_or_create(
                habit=habit, date=current_date, user=request.user,
                defaults={'done': False}
            )
            new_state_for_js = 'not-done'

        elif action == 'none':
            # Delete the status object to represent an 'unmarked' state.
            HabitStatus.objects.filter(habit=habit, date=current_date, user=request.user).delete()
            # new_state_for_js remains 'none'.

        # Recalculate stats and prepare them for the response.
        # refresh_from_db() ensures the model instance has the latest data.
        habit.refresh_from_db()
        updated_stats = {
            'current_streak': habit.current_streak(),
            'best_streak': habit.best_streak(),
            'score': habit.score()
        }

        # Send a detailed JSON response back to the client.
        return JsonResponse({
            'status': 'success', 
            'new_state': new_state_for_js,
            'stats': updated_stats
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)