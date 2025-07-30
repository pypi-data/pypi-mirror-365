from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured

from django_drf_jwt.settings import api_settings


def payload_handler(user: User) -> dict[str, any]:
    """
    Create payload for authentication
    :param user:
    :return:
    """
    user_id_field = api_settings.JWT_USER_ID_FIELD
    if not user_id_field:
        user_id_field = "pk"
    user_secret_field = api_settings.JWT_USER_SECRET_FIELD
    if not user_secret_field:
        raise ImproperlyConfigured("JWT_USER_SECRET_FIELD must be defined in settings")
    if not getattr(user, user_secret_field, None):
        raise ImproperlyConfigured("User dont have specified secret field")

    return {
        "user_id": str(getattr(user, user_id_field, None)),
        "user_secret": str(getattr(user, user_secret_field, None)),
    }
