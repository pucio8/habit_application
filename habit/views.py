import calendar
from calendar import monthrange
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import HabitForm
from .models import Habit, HabitStatus


@login_required
def habit_list(request):
    """Render Habit list"""
    habits = Habit.objects.order_by('id')  # default PK
    return render(request, 'habit/habit_list.html', {'habits': habits})


@login_required
def habit_add(request):
    """
        Add habit to habit_ist

        Get - render habit post,
        Post-redirect to habit list and render message
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
    """Edit habit"""
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
    """Delete habit"""
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    if request.method == 'POST':
        habit.delete()
        messages.success(request, f"Habit '{habit.name}' has been deleted!")
        return redirect('habit_list')
    return render(request, 'habit/habit_delete_confirm.html', {'habit': habit})


@login_required
def habit_detail(request, pk):
    """
        Displays the habit details for a specific month.

        Retrieves the habit, its statuses for the current month, and prepares data for rendering the calendar view.
        Only accessible by logged-in users.
        """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    today = date.today()
    current_day = today.day
    year = today.year
    month = today.month
    month_name = calendar.month_name[month]
    first_weekday, num_days = monthrange(year, month)  # 0-M, 1-T, ... 6-Sunday
    statuses = HabitStatus.objects.filter(
        habit=habit,
        user=request.user,
        date__year=year,
        date__month=month
    )
    # eg. status_dict = {1:True, 2:False .....}
    status_dict = {status.date.day: status.done for status in statuses}
    return render(request, 'habit/habit_detail.html', {
        'habit': habit,
        'status_dict': status_dict,
        'days': range(1, num_days + 1),
        'year': year,
        'month': month,
        'month_name': month_name,
        'today': current_day,
        'first_weekday': first_weekday,
    })


@require_POST
def update_habit_calendar(request, pk):
    """
        Updates or deletes a habit's status for a specific day.

        Receives a POST request with the 'day' and 'action' parameters ('done', 'not_done', 'none').
        Updates or deletes the corresponding HabitStatus entry for the authenticated user.

        Redirects to the habit detail page after the update.
        """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    day = int(request.POST.get('day'))  # eg. 9
    action = request.POST.get('action')  # 'done', 'not_done', 'none'
    today = date.today()
    chosen_date = date(today.year, today.month, day)
    if action not in ['done', 'not_done', 'none']:
        return redirect('habit_detail', pk=habit.pk)
    if action == 'none':
        HabitStatus.objects.filter(user=request.user, habit=habit, date=chosen_date).delete()
    else:
        status, _ = HabitStatus.objects.get_or_create(
            user=request.user,
            habit=habit,
            date=chosen_date
        )
        # Pass True or False
        status.done = (action == 'done')
        status.save()

    return redirect('habit_detail', pk=habit.pk)


@login_required
def more(request):
    """
    Render more.html
    (request for opinion)
    """
    return render(request, 'habit/more.html', {})
