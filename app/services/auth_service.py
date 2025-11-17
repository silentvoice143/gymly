from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models.user import User
from datetime import datetime, timedelta
import jwt
from app.config.settings import Config


class AuthService:

    @staticmethod
    def signup(name, email, password):
        if User.query.filter_by(email=email).first():
            return None, "Email already exists"

        hashed_pw = generate_password_hash(password)

        user = User(
            name=name,
            email=email,
            password=hashed_pw,
            role="user"
        )

        db.session.add(user)
        db.session.commit()

        return user, None

    @staticmethod
    def login(email, password):
        user = User.query.filter_by(email=email).first()
        if not user:
            return None, "Invalid email or password"

        if not check_password_hash(user.password, password):
            return None, "Invalid email or password"

        token = jwt.encode({
            "user_id": user.id,
            "role": user.role,
            "exp": datetime.utcnow() + timedelta(days=1)
        }, Config.JWT_SECRET, algorithm="HS256")

        return {"token": token, "user": {"id": user.id, "email": user.email}}, None
