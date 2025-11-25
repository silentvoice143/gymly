from flask import request
from datetime import datetime
from app.extensions import db
from app.models.gym import Gym
from app.models.user import User
from app.models.gym_enrollment import GymEnrollment

def paginate_query(query, page=1, per_page=20):
    """
    Paginate a SQLAlchemy query.
    """
    page = max(int(page), 1)
    per_page = max(int(per_page), 1)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    total_pages = (total + per_page - 1) // per_page
    return {
        "items": items,
        "total": total,
        "total_pages": total_pages,
        "page": page,
        "per_page": per_page
    }

class GymService:

    # ---------------------- GYM OWNER METHODS ----------------------
    @staticmethod
    def create_gym(data):
        owner = getattr(request, "current_user", None)
        if not owner:
            return None, "User not authenticated"
        if owner.role != "gym_owner":
            return None, "Only gym owners can create gyms"
        if not owner.is_subscription_active:
            return None, "Subscription inactive. Please subscribe"

        name = data.get("name")
        location = data.get("location")
        if not name or not location:
            return None, "Name and location are required"

        gym = Gym(name=name.strip(), location=location.strip(), owner_id=owner.id)
        db.session.add(gym)
        db.session.commit()
        return gym, None

    @staticmethod
    def update_gym(gym_id, data):
        owner = getattr(request, "current_user", None)
        if not owner:
            return None, "User not authenticated"

        gym = Gym.query.get(gym_id)
        if not gym:
            return None, "Gym not found"
        if gym.owner_id != owner.id:
            return None, "Access denied: Not gym owner"

        if "name" in data:
            gym.name = data["name"].strip()
        if "location" in data:
            gym.location = data["location"].strip()

        db.session.commit()
        return gym, None

    @staticmethod
    def delete_gym(gym_id):
        owner = getattr(request, "current_user", None)
        if not owner:
            return None, "User not authenticated"

        gym = Gym.query.get(gym_id)
        if not gym:
            return None, "Gym not found"
        if gym.owner_id != owner.id:
            return None, "Access denied: Not gym owner"

        db.session.delete(gym)
        db.session.commit()
        return {"message": "Gym deleted successfully"}, None

    @staticmethod
    def get_gym_members(gym_id, page=1, per_page=20):
        owner = getattr(request, "current_user", None)
        if not owner:
            return None, "User not authenticated"

        gym = Gym.query.get(gym_id)
        if not gym:
            return None, "Gym not found"
        if gym.owner_id != owner.id:
            return None, "Access denied: Not gym owner"

        query = GymEnrollment.query.filter_by(gym_id=gym_id)
        pagination = paginate_query(query, page, per_page)

        members = [
            {
                "id": e.user.id,
                "name": e.user.name,
                "email": e.user.email,
                "phone": e.user.phone,
                "enrolled_at": e.enrolled_at.isoformat(),
                "valid_till": e.valid_till.isoformat() if e.valid_till else None,
                "is_active": e.is_active
            }
            for e in pagination["items"]
        ]

        return {
            "members": members,
            "total": pagination["total"],
            "total_pages": pagination["total_pages"],
            "page": pagination["page"],
            "per_page": pagination["per_page"]
        }, None

    # ---------------------- PUBLIC METHODS ----------------------
    @staticmethod
    def get_all_gyms(page=1, per_page=20):
        query = Gym.query
        pagination = paginate_query(query, page, per_page)

        gyms_list = [
            {
                "id": gym.id,
                "name": gym.name,
                "location": gym.location,
                "owner_id": gym.owner_id,
                "owner_name": gym.owner.name if gym.owner else None
            }
            for gym in pagination["items"]
        ]

        return {
            "gyms": gyms_list,
            "total": pagination["total"],
            "total_pages": pagination["total_pages"],
            "page": pagination["page"],
            "per_page": pagination["per_page"]
        }

    @staticmethod
    def get_gym_by_id(gym_id):
        gym = Gym.query.get(gym_id)
        if not gym:
            return None, "Gym not found"
        return {
            "id": gym.id,
            "name": gym.name,
            "location": gym.location,
            "owner_id": gym.owner_id,
            "owner_name": gym.owner.name if gym.owner else None
        }, None

    # ---------------------- USER METHODS ----------------------
    @staticmethod
    def enroll_at_gym(data):
        user = getattr(request, "current_user", None)
        if not user:
            return None, "User not authenticated"

        gym_id = data.get("gym_id")
        if not gym_id:
            return None, "gym_id is required"

        gym = Gym.query.get(gym_id)
        if not gym:
            return None, "Gym not found"

        existing = GymEnrollment.query.filter_by(user_id=user.id, gym_id=gym_id, is_active=True).first()
        if existing:
            return None, "User already enrolled"

        enrollment = GymEnrollment(
            user_id=user.id,
            gym_id=gym_id,
            enrolled_at=datetime.utcnow(),
            valid_till=None,
            is_active=True
        )

        db.session.add(enrollment)
        db.session.commit()
        return {"message": f"User {user.name} enrolled in gym {gym.name}"}, None

    @staticmethod
    def unenroll_from_gym(data):
        user = getattr(request, "current_user", None)
        if not user:
            return None, "User not authenticated"

        gym_id = data.get("gym_id")
        if not gym_id:
            return None, "gym_id is required"

        enrollment = GymEnrollment.query.filter_by(user_id=user.id, gym_id=gym_id, is_active=True).first()
        if not enrollment:
            return None, "User is not enrolled in this gym"

        enrollment.is_active = False
        db.session.commit()
        return {"message": f"User {user.name} unenrolled from gym {enrollment.gym.name}"}, None

    @staticmethod
    def get_my_gyms(page=1, per_page=20):
        user = getattr(request, "current_user", None)
        if not user:
            return None, "User not authenticated"

        query = GymEnrollment.query.filter_by(user_id=user.id)
        pagination = paginate_query(query, page, per_page)

        gyms_list = [
            {
                "id": e.gym.id,
                "name": e.gym.name,
                "location": e.gym.location,
                "owner_id": e.gym.owner_id,
                "owner_name": e.gym.owner.name if e.gym.owner else None,
                "enrolled_at": e.enrolled_at.isoformat(),
                "valid_till": e.valid_till.isoformat() if e.valid_till else None,
                "is_active": e.is_active
            }
            for e in pagination["items"]
        ]

        return {
            "gyms": gyms_list,
            "total": pagination["total"],
            "total_pages": pagination["total_pages"],
            "page": pagination["page"],
            "per_page": pagination["per_page"]
        }
