from datetime import datetime
from passlib.hash import pbkdf2_sha256 as hasher
from app.extensions import db
from app.models.gym_enrollment import GymEnrollment


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="user", nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    # Subscription fields
    is_subscription_active = db.Column(db.Boolean, default=False)
    trial_started_at = db.Column(db.DateTime, nullable=True)
    trial_ends_at = db.Column(db.DateTime, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    gyms_owned = db.relationship("Gym", back_populates="owner")  # gyms this user owns
    enrollments = db.relationship("GymEnrollment", back_populates="user")

    bookings = db.relationship("Booking", back_populates="user")
    attendance_records = db.relationship("Attendance", back_populates="user")

    # Password helpers
    def set_password(self, password):
        self.password = hasher.hash(password)

    def check_password(self, password):
        return hasher.verify(password, self.password)

    # Serialize user safely
    def to_dict(self):
     return {
        "id": self.id,
        "name": self.name,
        "email": self.email,
        "phone": self.phone,
        "role": self.role,
        "is_subscription_active": self.is_subscription_active,
        "is_active": self.is_active,
        "trial_started_at": self.trial_started_at.isoformat() if self.trial_started_at else None,
        "trial_ends_at": self.trial_ends_at.isoformat() if self.trial_ends_at else None,
        "gyms_owned": [gym.id for gym in self.gyms_owned],
        "enrollments": [
            {
                "gym_id": e.gym_id,
                "enrolled_at": e.enrolled_at.isoformat(),
                "is_active": e.is_active
            } for e in self.enrollments
        ],
        "created_at": self.created_at.isoformat() if self.created_at else None,
    }
