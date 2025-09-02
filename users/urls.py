# in users/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# The CustomPasswordResetForm is not directly used here, but custom views
# that use it are. This import can be removed if not needed for clarity.
# from .forms import CustomPasswordResetForm

urlpatterns = [
    # --- Main Account Management ---
    path('resend-activation/', views.resend_activation_email, name='resend_activation'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('account/', views.account, name='account'),
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    
    # --- Password Reset Flow ---
    # This flow uses a combination of custom and built-in Django views
    # to handle password recovery.

    # Step 1: Form to request a password reset (user enters their email).
    path(
        'reset-password/', 
        views.CustomPasswordResetView.as_view(), # Use our custom view
        name='password_reset'
    ),
    # Step 2: Confirmation page shown after the reset email has been sent.
    path(
        'reset-password-done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/registration/password_reset_done.html"
        ), 
        name='password_reset_done'
    ),
    # Step 3: The link from the email, where the user sets a new password.
    path(
        'reset/<uidb64>/<token>/', 
        views.CustomPasswordResetConfirmView.as_view(), # Use our custom view
        name='password_reset_confirm'
    ),
    # # --- DODAJ TĘ NOWĄ ŚCIEŻKĘ PONIŻEJ ---
    # # Ścieżka nr 2: Adres, na który Django przekierowuje po weryfikacji tokenu
    # path(
    #     'reset/<uidb64>/set-password/',
    #     views.CustomPasswordResetConfirmView.as_view(),
    #     name='password_reset_set_password' # Dajemy inną nazwę dla porządku
    # ),
    # Step 4: Confirmation page shown after the password has been successfully changed.
    path(
        'reset-complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/registration/password_reset_complete.html"
        ), 
        name='password_reset_complete'
    ),
]