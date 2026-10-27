from datetime import datetime, timedelta, timezone as dt_timezone
from functools import wraps

import jwt
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone


JWT_ALGORITHM = "HS256"


def create_access_token(user):
    now = datetime.now(dt_timezone.utc)

    payload = {
        "user_id": user.user_id,
        "iat": now,
        "exp": now + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_MINUTES
        ),
    }

    return jwt.encode(
        payload,
        settings.JWT_SIGNING_KEY,
        algorithm=JWT_ALGORITHM,
    )


def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return JsonResponse(
                {"error": "Authentication token required"},
                status=401,
            )

        token = parts[1]

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SIGNING_KEY,
                algorithms=[JWT_ALGORITHM],
                options={"require": ["user_id", "iat", "exp"]},
            )
        except jwt.ExpiredSignatureError:
            return JsonResponse(
                {"error": "Access token has expired"},
                status=401,
            )
        except jwt.InvalidTokenError:
            return JsonResponse(
                {"error": "Invalid access token"},
                status=401,
            )

        user_id = payload["user_id"]

        if (
            isinstance(user_id, bool)
                or not isinstance(user_id, int)
                or user_id <= 0
        ):
            return JsonResponse(
                {"error": "Invalid access token"},
                    status=401,
            )
        
        from .models import User

        try:
            user = User.objects.get(
                user_id=payload["user_id"]
            )
        except (User.DoesNotExist, TypeError, ValueError):
            return JsonResponse(
                {"error": "User not found"},
                status=401,
            )
            
        if timezone.now() >= user.valid_until:
            return JsonResponse(
            {
                "status": "error",
                "code": "account_expired",
                "error": "Your account has expired. Please reactivate your account.",
            },
            status=403,
        )

        # Attach the verified database user to this request.
        request.authenticated_user = user

        return view_func(request, *args, **kwargs)

    return wrapper