from datetime import datetime, timedelta
from app.extensions import db
from app.models.user import User
from app.services.jwt_service import JWTService


class AuthService:
    @staticmethod
    def signup(name, email, password):
      email = email.lower().strip()

      if User.query.filter_by(email=email).first():
        return None, "Email already exists"

      user = User(
        name=name,
        email=email,
        role="user",
        is_subscription_active=False,
        trial_started_at=None,
        trial_ends_at=None
    )

      user.set_password(password)

      db.session.add(user)
      db.session.commit()

      return user, None

@staticmethod
def signup_gym_owner(name, email, password):
    email = email.lower().strip()

    if User.query.filter_by(email=email).first():
        return None, "Email already exists"

    now = datetime.utcnow()

    # Gym owner gets a 1-month free trial
    user = User(
        name=name,
        email=email,
        role="gym_owner",
        is_subscription_active=True,  # active during trial
        trial_started_at=now,
        trial_ends_at=now + timedelta(days=30)  # <-- 1 month trial
    )

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
