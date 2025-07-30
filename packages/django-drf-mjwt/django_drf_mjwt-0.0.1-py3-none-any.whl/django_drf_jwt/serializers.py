import jwt
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone
from rest_framework import serializers

from django_drf_jwt.handlers import payload_handler
from django_drf_jwt.settings import api_settings


class JwtAuthSerializer(serializers.Serializer):

    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
    token = serializers.CharField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(JwtAuthSerializer, self).__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField(write_only=True, required=True)

    @property
    def username_field(self):
        return get_user_model().USERNAME_FIELD

    def validate(self, attrs):
        username = attrs.get(self.username_field)
        if not username:
            raise serializers.ValidationError("username is required")
        password = attrs.get("password", None)
        if not password:
            raise serializers.ValidationError("password is required")

        credentials = {self.username_field: username, "password": password}

        user = authenticate(**credentials)
        if not user:
            raise serializers.ValidationError("Unable to authenticate with provided credentials")

        token = jwt.encode(self.get_payload_handler(user), api_settings.JWT_SECRET, algorithm="HS256")
        return {
            "token": token,
            "created": timezone.now(),
        }

    @classmethod
    def get_payload_handler(cls, *args, **kwargs) -> dict[str, any]:
        return (
            api_settings.JWT_PAYLOAD_HANDLER(*args, **kwargs)
            if api_settings.JWT_PAYLOAD_HANDLER
            else payload_handler(*args, **kwargs)
        )
