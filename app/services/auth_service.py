from datetime import datetime, timedelta
import jwt

from app.extensions import db
from app.models.user import User
from app.config.settings import Config
from app.services.jwt_service import JWTService


class AuthService:

    @staticmethod
    def signup(name, email, password):
        email = email.lower().strip()

        # check if email exists
        if User.query.filter_by(email=email).first():
            return None, "Email already exists"

        # Create user object
        user = User(
            name=name,
            email=email,
            role="user"
        )

        # Use User model method to hash password
        user.set_password(password)

        # 2-month free trial (Gymly feature)
        now = datetime.utcnow()
        user.is_subscription_active = True
        user.trial_started_at = now
        user.trial_ends_at = now + timedelta(days=60)

        db.session.add(user)
        db.session.commit()

        return user, None

    @staticmethod
    def signup_gym_owner(name, email, password):
        email = email.lower().strip()

        if User.query.filter_by(email=email).first():
            return None, "Email already exists"

        user = User(
            name=name,
            email=email,
            role="gym_owner"
        )

        # Use helper
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return user, None

    @staticmethod
    def login(email, password):
        email = email.lower().strip()

        user = User.query.filter_by(email=email).first()
        if not user:
            return None, "Invalid email or password"

        # Use helper to check password
        if not user.check_password(password):
            return None, "Invalid email or password"

        # Create JWT token
        token = JWTService.create_access_token({
            "user_id": user.id,
            "role": user.role,
        })
       

        # Build response
        return {
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "is_subscription_active": user.is_subscription_active,
                "trial_started_at": user.trial_started_at.isoformat() if user.trial_started_at else None,
                "trial_ends_at": user.trial_ends_at.isoformat() if user.trial_ends_at else None
            }
        }, None
