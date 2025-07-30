import jwt
from django.contrib.auth import get_user_model
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed

from django_drf_jwt.settings import api_settings


class JWTAuthentication(BasicAuthentication):
    """
    JWT authentication - django-drf-jwt authentication for user
    this class is responsible to authenticate user
    """

    @staticmethod
    def get_token(request):
        token = request.META.get("HTTP_AUTHORIZATION")
        if not token:
            return None

        token = token.split(" ")
        if len(token) != 2:
            return None
        if token[0].strip().lower() != api_settings.JWT_AUTH_HEADER_PREFIX.lower():
            return None
        return token[1]

    @classmethod
    def decode_token_from_header(cls, token: str) -> tuple[str, str]:
        if not token:
            raise AuthenticationFailed("No token provided")
        decoded_token = jwt.decode(token, api_settings.JWT_SECRET, algorithms=["HS256"])
        return decoded_token["user_id"], decoded_token["user_secret"]

    def authenticate(self, request):
        token = self.get_token(request)
        user_id, secret = self.decode_token_from_header(token)
        query = {api_settings.JWT_USER_ID_FIELD: user_id}
        try:
            user = get_user_model().objects.get(**query)
        except get_user_model().DoesNotExist:
            raise AuthenticationFailed("Could not validate credentials")

        if not self.user_can_authenticate(user):
            raise AuthenticationFailed("Could not validate credentials")

        # user_secret must be the same!
        if secret != str(getattr(user, api_settings.JWT_USER_SECRET_FIELD, None)):
            raise AuthenticationFailed("Could not validate credentials")
        return user, token

    @classmethod
    def user_can_authenticate(cls, user: any) -> bool:
        """This can be overwritten by your needs"""
        return user.is_active or user.is_superuser or user.is_staff
