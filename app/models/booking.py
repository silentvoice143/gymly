from app.extensions import db
from datetime import datetime

class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    gym_id = db.Column(db.Integer, db.ForeignKey("gyms.id"))
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="pending")  # pending, success, cancelled
    amount = db.Column(db.Float, default=0.0)

    user = db.relationship("User", back_populates="bookings")
    gym = db.relationship("Gym", back_populates="bookings")
