from django.shortcuts import redirect


def role_required(allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            profile = getattr(request.user, 'profile', None)

            if profile is None:
                return redirect('home')

            if profile.role not in allowed_roles:
                return redirect('home')

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator