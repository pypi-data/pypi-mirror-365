"""
Django settings for testing your package
"""

SECRET_KEY = "test-secret-key"

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "rest_framework",
    "tests",
    "django_drf_jwt",  # Your package
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "tests.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

USE_TZ = True


REST_FRAMEWORK = {"DEFAULT_AUTHENTICATION_CLASSES": ("django_drf_jwt.authentication.JWTAuthentication",)}

# JWT DATA
JWT_DRF = {
    # JWT_USER_SECRET_FIELD - MUST BE DEFINED - This must be filed in User object
    "JWT_USER_SECRET_FIELD": "secret",  # for testing purposes we can use last_name as secret field
}

AUTH_USER_MODEL = "tests.EmailUser"
