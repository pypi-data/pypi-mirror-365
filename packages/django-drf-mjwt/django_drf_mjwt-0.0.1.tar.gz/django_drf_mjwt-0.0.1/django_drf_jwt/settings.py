from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from rest_framework.settings import APISettings

USER_SETTINGS = getattr(settings, "JWT_DRF", None)

DEFAULTS = {
    "JWT_SECRET": settings.SECRET_KEY,
    "JWT_USER_ID_FIELD": "pk",
    "JWT_USER_SECRET_FIELD": None,  # MUST BE DEFINED - This must be a
    "JWT_PAYLOAD_HANDLER": "django_drf_jwt.handlers.payload_handler",
    "JWT_AUTH_HEADER_PREFIX": "JWT",
}

IMPORT_STRINGS = {
    "JWT_PAYLOAD_HANDLER",
}


api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)

if not api_settings.JWT_USER_SECRET_FIELD:
    raise ImproperlyConfigured("JWT_USER_SECRET_FIELD must be set in settings file")


if not getattr(get_user_model(), api_settings.JWT_USER_SECRET_FIELD, None):
    raise ImproperlyConfigured("User don't have secret field")
