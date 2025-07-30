import uuid

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django_drf_jwt.serializers import JwtAuthSerializer
from django_drf_jwt.settings import api_settings


class JWTAuthView(GenericAPIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()
    serializer_class = JwtAuthSerializer

    def post(self, request, *args, **kwargs):
        """
        Need to return token in response
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        created = serializer.validated_data["created"]
        return Response({"token": token, "created": created}, status=status.HTTP_201_CREATED)


class JWTRevokeTokenView(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        new_secret = str(uuid.uuid4())
        setattr(request.user, api_settings.JWT_USER_SECRET_FIELD, new_secret)
        request.user.save(update_fields=[api_settings.JWT_USER_SECRET_FIELD])
        return Response({}, status=status.HTTP_201_CREATED)
