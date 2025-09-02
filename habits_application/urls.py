from django.contrib import admin
from django.urls import path, include

# This is the main URL router for the entire project.
# It acts as a "switchboard," delegating requests to the appropriate app.

urlpatterns = [
    # 1. Admin Site URLs
    # Includes all the automatically generated URLs for the Django admin interface.
    path("admin/", admin.site.urls),
    
    # 2. User Account URLs
    # Delegates all URLs starting with 'accounts/' (e.g., /accounts/login/, /accounts/register/)
    path("accounts/", include('users.urls')),

    # 3. Main Application URLs
    # Delegates all other URLs to be handled by the urls.py file
    path("", include('habit.urls')),
]

# Custom Error Handlers
handler400 = 'habits_application.views.custom_400' # Bad Request
handler403 = 'habits_application.views.custom_403' # Forbidden
handler404 = 'habits_application.views.custom_404' # Not Found
handler500 = 'habits_application.views.custom_500' # Server Error