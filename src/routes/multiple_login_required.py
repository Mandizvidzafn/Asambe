from functools import wraps
from flask import redirect, url_for
from flask_login import current_user


def login_required_with_manager(login_manager):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for(login_manager.login_view))
            return view_func(*args, **kwargs)

        return wrapper

    return decorator
