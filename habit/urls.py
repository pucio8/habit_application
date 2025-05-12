from django.urls import path
from . import views
from .views import CustomPasswordChangeView

urlpatterns = [
    path('', views.habit_list, name='habit_list'),
    path('habit_add/', views.habit_add, name='habit_add'),
    path('habit/<int:pk>/', views.habit_detail, name='habit_detail'),
    path('habit/<int:pk>/edit', views.habit_edit, name='habit_edit'),
    path('habit/<int:pk>/delete/', views.habit_delete, name='habit_delete'),
    path('more', views.more, name='more'),
    path('settings/', views.settings_view, name='settings'),
    path('cache-test/', views.cache_test, name='cache_test'),
    path('habit/<int:pk>/calendar/', views.habit_detail, name='habit_calendar'),
    path('habit/<int:pk>/calendar/update/', views.update_habit_calendar, name='update_habit_calendar'),
    path('change-password/', CustomPasswordChangeView.as_view(), name='change_password'),
]
