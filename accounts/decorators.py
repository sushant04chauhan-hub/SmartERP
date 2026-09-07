from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def role_required(*allowed_roles):
    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:
                return redirect("login")

            # Django superusers always have full access
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            profile = getattr(request.user, "profile", None)

            if profile is None:
                raise PermissionDenied(
                    "Your account does not have a user profile."
                )

            if profile.role not in allowed_roles:
                raise PermissionDenied(
                    "You do not have permission to access this page."
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator