from django.contrib import admin

from habit.models import Habit, HabitStatus

admin.site.register(Habit)

@admin.register(HabitStatus)
class HabitStatus(admin.ModelAdmin):
    list_display = ('user', 'habit', 'date', 'done') #record list
    list_filter = ('done', 'date', 'habit') #later add user
    search_fields = ('habit__name', 'user__username')