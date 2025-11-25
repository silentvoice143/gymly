from app.extensions import db
from datetime import datetime,date

class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    gym_id = db.Column(db.Integer, db.ForeignKey("gyms.id"))
    date = db.Column(db.Date, default=date.today, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="attendance_records")
    gym = db.relationship("Gym", back_populates="attendance_records")
 

    __table_args__ = (
        db.UniqueConstraint('user_id', 'gym_id', 'date', name='unique_daily_attendance'),
    )