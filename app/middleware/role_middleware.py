from flask import jsonify
from app.middleware.auth_middleware import token_required

def require_role(role):
    def decorator(fn):
        @token_required
        def wrapper(current_user, *args, **kwargs):
            if current_user.role != role:
                return jsonify({"error": "Access denied"}), 403

            return fn(current_user, *args, **kwargs)
        wrapper.__name__ = fn.__name__
        return wrapper
    return decorator

# from functools import wraps
# from flask import request
# import jwt
# from app.config.settings import Config
# from app.models.user import User

# def require_role(*roles):
#     def decorator(fn):
#         @wraps(fn)
#         def wrapper(*args, **kwargs):
#             auth_header = request.headers.get("Authorization")

#             if not auth_header or not auth_header.startswith("Bearer "):
#                 return {"error": "Authorization token required"}, 401

#             token = auth_header.split(" ")[1]
#             try:
#                 data = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
#                 user = User.query.get(data["user_id"])
#             except Exception:
#                 return {"error": "Invalid or expired token"}, 401

#             if user.role not in roles:
#                 return {"error": "Access denied"}, 403

#             return fn(user, *args, **kwargs)
#         return wrapper
#     return decorator

