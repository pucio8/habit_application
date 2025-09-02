from pathlib import Path
import environ
import sys


# Step 1: Initialize django-environ
# ==============================================================================
env = environ.Env(
    # Set casting and default values for key variables
    DEBUG=(bool, False) # Automatically cast DEBUG to a boolean (True/False)
)


# Step 2: Set paths and read the .env file
# ==============================================================================
# BASE_DIR points to the project's root folder (where manage.py is)
BASE_DIR = Path(__file__).resolve().parent.parent

# Read environment variables from the .env file. This replaces load_dotenv()
environ.Env.read_env(BASE_DIR / ".env")


# Step 3: Core Security Settings
# ==============================================================================
# WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['127.0.0.1', 'localhost'])


# Step 4: Application & Middleware Definitions
# ==============================================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    # External Apps
    "django.contrib.staticfiles",
    # Local Apps
    "widget_tweaks",
    "habit.apps.HabitConfig", # Explicit app config
    "users.apps.UsersConfig", # Explicit app config

]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "habit_application.urls"
WSGI_APPLICATION = "habit_application.wsgi.application"


# Step 5: Templates Configuration
# ==============================================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"], # Points to the global templates directory
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# Step 6: Database Configuration
# ==============================================================================
DATABASES = {
    # env.db() is a powerful function that can parse a full DATABASE_URL string,
    # e.g., mysql://user:password@host:port/name
    # But for readability, we can also read each variable separately:
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env.int('DB_PORT', default=3306),
    }
}

# Switch to an in-memory SQLite database when running tests
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }


# Step 7: Authentication Settings
# ==============================================================================
AUTH_USER_MODEL = "users.CustomUser"
AUTHENTICATION_BACKENDS = [
    'users.backends.EmailOrUsernameBackend',
    'django.contrib.auth.backends.ModelBackend',
]
LOGIN_REDIRECT_URL = "habit_list"
LOGOUT_REDIRECT_URL = "login"
LOGIN_URL = "login"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Step 8: Internationalization & Static Files
# ==============================================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Warsaw"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Step 9: Email Settings
# ==============================================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default=None)
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default=None)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)
EMAIL_SUBJECT_PREFIX = env('EMAIL_SUBJECT_PREFIX', default='[Habit Tracker]')


# Step 10: Cache Settings
# ==============================================================================
USE_REDIS_CACHE = env.bool('USE_REDIS_CACHE', default=False)

if USE_REDIS_CACHE:
    CACHES = {
        # A Redis configuration could be placed here in the future
        "default": {
            "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
            "LOCATION": BASE_DIR / "cache_data",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": 'django.core.cache.backends.dummy.DummyCache',
        }
    }