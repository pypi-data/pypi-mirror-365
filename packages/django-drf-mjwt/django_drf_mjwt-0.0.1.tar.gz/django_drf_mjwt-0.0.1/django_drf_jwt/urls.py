from django.urls import path

from django_drf_jwt.views import JWTAuthView, JWTRevokeTokenView

app_name = "django_drf_jwt"

urlpatterns = [
    path("get_token/", JWTAuthView.as_view(), name="get_token"),
    path("revoke/", JWTRevokeTokenView.as_view(), name="revoke_token"),
]
