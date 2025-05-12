from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from habit import views
from habit.views import CustomPasswordResetConfirmView

urlpatterns = [
    path('', include('habit.urls')),
    path("admin/", admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('reset-password/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset-password-done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]

handler404 = 'habit.views.custom_404'
handler500 = 'habit.views.custom_500'
handler403 = 'habit.views.custom_403'
handler400 = 'habit.views.custom_400'
