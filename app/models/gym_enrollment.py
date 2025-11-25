# association.py or at the top of models/user.py
from app.extensions import db
from datetime import datetime

class GymEnrollment(db.Model):
    __tablename__ = "gym_enrollments"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    gym_id = db.Column(db.Integer, db.ForeignKey("gyms.id"))

    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    valid_till = db.Column(db.DateTime)  # subscription or booking duration
    is_active = db.Column(db.Boolean, default=True)

    user = db.relationship("User", back_populates="enrollments")
    gym = db.relationship("Gym", back_populates="enrollments")

