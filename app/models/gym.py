from app.extensions import db
# Association table for gym members


class Gym(db.Model):
    __tablename__ = "gyms"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    # Relationships
    owner = db.relationship("User", back_populates="gyms")
    bookings = db.relationship("Booking", back_populates="gym")
    attendance_records = db.relationship("Attendance", back_populates="gym")
    enrollments = db.relationship("GymEnrollment", back_populates="gym")

