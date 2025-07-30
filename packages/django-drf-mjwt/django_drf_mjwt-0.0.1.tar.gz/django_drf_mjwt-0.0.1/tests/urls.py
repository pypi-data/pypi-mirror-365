from django.urls import path

from django_drf_jwt.views import JWTAuthView, JWTRevokeTokenView

urlpatterns = [
    path("get_token/", JWTAuthView.as_view(), name="get_token"),
    path("revoke/", JWTRevokeTokenView.as_view(), name="revoke_token"),
]
