from functools import wraps
from flask import request, jsonify
from app.middleware.auth_middleware import token_required

def require_role(role):
    """
    Decorator to restrict access to users with a specific role.
    Works with token_required to ensure authentication first.
    """

    def decorator(fn):
        @wraps(fn)
        @token_required  # ensure user is authenticated
        def wrapper(*args, **kwargs):
            user = getattr(request, "current_user", None)

            if not user:
                return jsonify({"error": "Authentication required"}), 401

            if user.role != role:
                return jsonify({"error": "Access denied"}), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator
