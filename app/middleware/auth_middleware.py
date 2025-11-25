from flask import request, jsonify
from app.models.user import User
from app.services.jwt_service import JWTService
from functools import wraps
from jwt import ExpiredSignatureError, InvalidTokenError

def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization required"}), 401

        token = auth_header.split(" ")[1]

        try:
            data = JWTService.decode_token(token)
            user = User.query.get(data.get("user_id"))
            if not user:
                return jsonify({"error": "User not found"}), 404
        except ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        # Attach user to request for downstream use
        request.current_user = user

        return fn(*args, **kwargs)

    return wrapper
