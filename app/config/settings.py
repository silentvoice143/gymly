import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:password@localhost:5432/gymly"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET = os.getenv("JWT_SECRET", "jwt-dev-secret")

    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@localhost/")
