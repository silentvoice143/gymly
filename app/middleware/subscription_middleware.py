from functools import wraps
from flask import request
from datetime import datetime
from app.models.user import User
from app.services.jwt_service import JWTService

def subscription_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):

        # 1. Read token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"error": "Missing or invalid authorization token"}, 401

        token = auth_header.split(" ")[1]

        # 2. Decode JWT
        payload = JWTService.decode_access_token(token)
        if not payload:
            return {"error": "Invalid or expired token"}, 401

        user = User.query.get(payload.get("user_id"))
        if not user:
            return {"error": "User not found"}, 404

        # 3. Only gym owners can require subscription
        if user.role != "gym_owner":
            return {"error": "Only gym owners have subscriptions"}, 403

        # 4. Auto-expire trial if needed
        if user.trial_ends_at and datetime.utcnow() > user.trial_ends_at:
            if user.is_subscription_active:  # only update if still marked active
                user.is_subscription_active = False
                from app.extensions import db
                db.session.commit()

        # 5. Check subscription status
        if not user.is_subscription_active:
            return {"error": "Subscription inactive. Please subscribe to continue"}, 403

        # Attach user to request for convenience
        request.current_user = user

        return fn(*args, **kwargs)

    return wrapper
