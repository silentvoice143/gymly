from app.extensions import db
from datetime import datetime

class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    gym_id = db.Column(db.Integer, db.ForeignKey("gyms.id"))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="attendance_records")
    gym = db.relationship("Gym", back_populates="attendance_records")
