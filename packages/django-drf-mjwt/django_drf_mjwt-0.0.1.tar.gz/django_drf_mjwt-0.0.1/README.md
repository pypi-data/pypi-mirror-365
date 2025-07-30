# Django DRF JWT

Goal of this simple package is to create a simple JWT authentication for Django apps.
This should be easy to configue and easy to adapt to your needs and preferences.
Package is based on [PyJWT](https://github.com/jpadilla/pyjwt)


## Setup

1. Install package
    ```shell
    pip install django-drf-mjwt
    ```

2. Add django_drf_jwt to your INSTALLED_APPS:
   ```python
   INSTALLED_APPS = [
    # ...
    "django_drf_jwt",
    # ...
    ]
   ```

3. Update REST_FRAMEWORK settings:
    ```python
    REST_FRAMEWORK = {
        # ...
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "django_drf_jwt.authentication.JWTAuthentication",
        )
        # ...
    }
    ```

4. Add new field in your User model and add this to your settings file
    ```python
    JWT_DRF = {
        # JWT_USER_SECRET_FIELD - MUST BE DEFINED - This must be filed in User object
        "JWT_USER_SECRET_FIELD": "secret",
    }
    ```

    Available settings:
    ```python
    # These are default settings
    JWT_DRF = {
        "JWT_SECRET": settings.SECRET_KEY,
        "JWT_USER_ID_FIELD": "pk",
        "JWT_USER_SECRET_FIELD": None,  # MUST BE DEFINED - This must be a
        "JWT_PAYLOAD_HANDLER": "django_drf_jwt.handlers.payload_handler",
        "JWT_AUTH_HEADER_PREFIX": "JWT",
    }
    ```

## Developing

To setup environment for local developing install requirements from `requirements.txt` file.
Make sure that you write tests for your implementation.


### Issues
If you have any suggestions or you see some issues and bugs be free to contact me!
