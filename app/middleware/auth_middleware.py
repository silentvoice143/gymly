from flask import request, jsonify
import jwt
from app.config.settings import Config
from app.models.user import User


def token_required(fn):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization required"}), 401

        token = auth_header.split(" ")[1]

        try:
            data = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
            user = User.query.get(data["user_id"])
        except Exception:
            return jsonify({"error": "Invalid or expired token"}), 401

        return fn(user, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper
