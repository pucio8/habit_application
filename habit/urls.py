from django.urls import path
from . import views

urlpatterns = [
    path('', views.habit_list, name='habit_list'),
    path('habit_add/', views.habit_add, name='habit_add'),
    path('habit/<int:pk>/', views.habit_detail, name='habit_detail'),
    path('habit/<int:pk>/edit', views.habit_edit, name='habit_edit'),
    path('habit/<int:pk>/delete/', views.habit_delete, name='habit_delete'),
    path('habit/<int:pk>/calendar/', views.update_habit_calendar, name='update_habit_calendar'),
    path('more', views.more, name='more'),
    path('settings/', views.settings_view, name='settings'),
]
