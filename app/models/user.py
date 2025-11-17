from app.extensions import db
from passlib.hash import pbkdf2_sha256 as hasher

class User(db.Model):
    __tablename__="users"

    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(150),nullable=False)
    email=db.Column(db.String(150),unique=True,nullable=False)
    password=db.Column(db.String(255),nullable=False)
    role=db.Column(db.String(50),default="user")

    #Relationships
    gyms=db.relationship("Gym",back_populates="owner")
    bookings=db.relationship("Booking",back_populates="user")
    attendance_records=db.relationship("Attendance",back_populates="user")

    #Methods

    def set_password(self,password):
        self.password_hash=hasher.hash(password)
        
    def check_password(self,password):
        return hasher.verify(password,self.password_hash)