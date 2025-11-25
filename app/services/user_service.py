from flask import request
from app.models.user import User
from app.extensions import db
from app.models.gym import Gym
from app.models.gym_enrollment import GymEnrollment

def paginate_query(query, page=1, per_page=20):
    """
    Returns paginated results from a SQLAlchemy query.
    :param query: SQLAlchemy query
    :param page: current page number (1-based)
    :param per_page: number of items per page
    :return: dict with items, total count, total pages, current page
    """
    page = max(int(page), 1)
    per_page = max(int(per_page), 1)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    total_pages = (total + per_page - 1) // per_page  # ceil division
    return {
        "items": items,
        "total": total,
        "total_pages": total_pages,
        "page": page,
        "per_page": per_page
    }


class UserService:

    @staticmethod
    def get_profile():
        """
        Returns the profile of the currently authenticated user.
        Requires `token_required` decorator to have set request.current_user.
        """
        user = getattr(request, "current_user", None)
        if not user:
            return None, "User not authenticated"

        # Build response dictionary
        profile = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_subscription_active": user.is_subscription_active,
            "trial_started_at": user.trial_started_at.isoformat() if user.trial_started_at else None,
            "trial_ends_at": user.trial_ends_at.isoformat() if user.trial_ends_at else None
        }

        return profile, None
    

from flask import request
from app.models.user import User
from app.extensions import db

class UserService:

    @staticmethod
    def get_profile():
        """
        Returns the profile of the currently authenticated user.
        Requires `token_required` decorator to have set request.current_user.
        """
        user = getattr(request, "current_user", None)
        if not user:
            return None, "User not authenticated"

        profile = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_subscription_active": user.is_subscription_active,
            "trial_started_at": user.trial_started_at.isoformat() if user.trial_started_at else None,
            "trial_ends_at": user.trial_ends_at.isoformat() if user.trial_ends_at else None
        }

        return profile, None

    @staticmethod
    def update_profile(data):
        """
        Update profile fields of the currently authenticated user.
        data: dict containing keys like 'name' or 'email'
        """
        user = getattr(request, "current_user", None)
        if not user:
            return None, "User not authenticated"

        # Update name if provided
        if "name" in data:
            user.name = data["name"].strip()

        # Update email if provided
        if "email" in data:
            new_email = data["email"].lower().strip()
            # Check if email is already taken by another user
            if User.query.filter(User.email == new_email, User.id != user.id).first():
                return None, "Email already in use"
            user.email = new_email

        # Add more fields here if needed
        # e.g., user.phone = data.get("phone", user.phone)

        db.session.commit()

        # Return updated profile
        profile = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_subscription_active": user.is_subscription_active,
            "trial_started_at": user.trial_started_at.isoformat() if user.trial_started_at else None,
            "trial_ends_at": user.trial_ends_at.isoformat() if user.trial_ends_at else None
        }

        return profile, None
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get any user profile by ID"""
        user = User.query.get(user_id)
        if not user:
            return None, "User not found"

        profile = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_subscription_active": user.is_subscription_active,
            "trial_started_at": user.trial_started_at.isoformat() if user.trial_started_at else None,
            "trial_ends_at": user.trial_ends_at.isoformat() if user.trial_ends_at else None
        }

        return profile, None
    
    # ==================== Owner perceptive==================

def get_gym_members(gym_id, page=1, per_page=20):
    gym = Gym.query.get(gym_id)
    if not gym:
        return None, "Gym not found"

    query = GymEnrollment.query.filter_by(gym_id=gym_id)
    pagination = paginate_query(query, page, per_page)

    members = [
        {
            "user_id": e.user_id,
            "name": e.user.name,
            "email": e.user.email,
            "phone": e.user.phone,
            "enrolled_at": e.enrolled_at.isoformat(),
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


def unenroll_user(gym_id, user_id):
    enrollment = GymEnrollment.query.filter_by(gym_id=gym_id, user_id=user_id, is_active=True).first()
    if not enrollment:
        return None, "Enrollment not found"
    enrollment.is_active = False
    db.session.commit()
    return {"message": f"User {user_id} unenrolled from gym {gym_id}"}, None

  
def set_enrollment_status(gym_id, user_id, status=True):
    enrollment = GymEnrollment.query.filter_by(gym_id=gym_id, user_id=user_id).first()
    if not enrollment:
        return None, "Enrollment not found"
    enrollment.is_active = status
    db.session.commit()
    return {"message": f"User {user_id} enrollment set to {status}"}, None



# ===============admin perceptive=============
def get_all_users_paginated(page=1, per_page=20):
    query = User.query
    pagination = paginate_query(query, page, per_page)

    users = [u.to_dict() for u in pagination["items"]]

    return {
        "users": users,
        "total": pagination["total"],
        "total_pages": pagination["total_pages"],
        "page": pagination["page"],
        "per_page": pagination["per_page"]
    }

def set_user_status(user_id, is_active):
    user = User.query.get(user_id)
    if not user:
        return None, "User not found"
    user.is_active = is_active
    db.session.commit()
    return {"message": f"User {user_id} active status set to {is_active}"}, None

def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return None, "User not found"
    db.session.delete(user)
    db.session.commit()
    return {"message": f"User {user_id} deleted successfully"}, None

