from datetime import datetime, timedelta
from jose import jwt, JWTError
from config.settings import Config


class JWTService:
    SECRET_KEY = Config.JWT_SECRET
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

    @classmethod
    def create_access_token(cls, data: dict) -> str:
        """Generate JWT token with expiry."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode["exp"] = expire
        token = jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return token

    @classmethod
    def decode_token(cls, token: str) -> dict:
        """Decode JWT token and return payload."""
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            return payload
        except JWTError:
            return None
