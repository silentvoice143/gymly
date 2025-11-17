from app.extensions import db
from datetime import datetime, timedelta

class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)

    plan = db.Column(db.String(50))  # free, monthly, yearly

    user = db.relationship("User")

    @staticmethod
    def trial_period():
        return datetime.utcnow() + timedelta(days=60)
