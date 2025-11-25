from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.user_service import UserService
from app.middleware.auth_middleware import token_required
from app.middleware.role_middleware import require_role

user_ns = Namespace("Users", description="User profile APIs")
enroll_ns = Namespace("Enrollments", description="Gym enrollment management APIs")

# -------------------- MODELS --------------------
update_profile_model = user_ns.model("UpdateProfileModel", {
    "name": fields.String(required=False),
    "email": fields.String(required=False),
})

set_status_model = user_ns.model("SetStatusModel", {
    "is_active": fields.Boolean(required=True)
})

set_enrollment_model = enroll_ns.model("SetEnrollmentModel", {
    "is_active": fields.Boolean(required=True)
})

# -------------------- PROFILE ROUTES --------------------
@user_ns.route("/profile")
class UserProfileAPI(Resource):
    
    @token_required
    def get(self):
        """Get current authenticated user's profile"""
        profile, error = UserService.get_profile()
        if error:
            return {"error": error}, 401
        return {"profile": profile}, 200

    @token_required
    @user_ns.expect(update_profile_model)
    def put(self):
        """Update current authenticated user's profile"""
        data = request.get_json()
        profile, error = UserService.update_profile(data)
        if error:
            return {"error": error}, 400
        return {"profile": profile, "message": "Profile updated successfully"}, 200

# -------------------- USER BY ID --------------------
@user_ns.route("/<int:user_id>/profile")
class UserProfileByIdAPI(Resource):
    
    @token_required
    @require_role("gym_owner")  # Adjust guard as needed
    def get(self, user_id):
        """Get profile of a user by ID"""
        profile, error = UserService.get_user_by_id(user_id)
        if error:
            return {"error": error}, 404
        return {"profile": profile}, 200

# -------------------- ADMIN ROUTES --------------------
@user_ns.route("/")
class UsersListAPI(Resource):

    @token_required
    @require_role("admin")
    def get(self):
        """Get paginated list of all users"""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        result = UserService.get_all_users_paginated(page, per_page)
        return result, 200

@user_ns.route("/<int:user_id>/status")
class UserStatusAPI(Resource):

    @token_required
    @require_role("admin")
    @user_ns.expect(set_status_model)
    def post(self, user_id):
        """Set user active/inactive status"""
        is_active = request.json.get("is_active", True)
        result, error = UserService.set_user_status(user_id, is_active)
        if error:
            return {"error": error}, 404
        return result, 200

@user_ns.route("/<int:user_id>")
class UserDeleteAPI(Resource):

    @token_required
    @require_role("admin")
    def delete(self, user_id):
        """Delete a user"""
        result, error = UserService.delete_user(user_id)
        if error:
            return {"error": error}, 404
        return result, 200

# -------------------- GYM OWNER ENROLLMENT ROUTES --------------------
@enroll_ns.route("/gym/<int:gym_id>/user/<int:user_id>/status")
class EnrollmentStatusAPI(Resource):

    @token_required
    @require_role("gym_owner")
    @enroll_ns.expect(set_enrollment_model)
    def post(self, gym_id, user_id):
        """Activate or deactivate a user's enrollment in a gym"""
        is_active = request.json.get("is_active", True)
        result, error = UserService.set_enrollment_status(gym_id, user_id, is_active)
        if error:
            return {"error": error}, 404
        return result, 200

@enroll_ns.route("/gym/<int:gym_id>/members")
class GymMembersAPI(Resource):

    @token_required
    @require_role("gym_owner")
    def get(self, gym_id):
        """Get paginated list of members for a gym"""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        result, error = UserService.get_gym_members(gym_id, page, per_page)
        if error:
            return {"error": error}, 404
        return result, 200

@enroll_ns.route("/gym/<int:gym_id>/user/<int:user_id>/unenroll")
class GymUnenrollAPI(Resource):

    @token_required
    @require_role("gym_owner")
    def post(self, gym_id, user_id):
        """Unenroll a user from a gym"""
        result, error = UserService.unenroll_user(gym_id, user_id)
        if error:
            return {"error": error}, 404
        return result, 200


"""
==========================
USER & ENROLLMENT API REFERENCE
==========================

USER PROFILE ROUTES
------------------
1. GET /users/profile
   - Purpose: Get current authenticated user's profile
   - Middleware: token_required
   - Response: User info (id, name, email, role, subscription, trial dates)

2. PUT /users/profile
   - Purpose: Update current authenticated user's profile
   - Middleware: token_required
   - Body: { "name": <optional>, "email": <optional> }
   - Response: Updated user profile

3. GET /users/<user_id>/profile
   - Purpose: Get another user's profile by ID
   - Middleware: token_required + require_role("gym_owner")
   - Response: User profile (id, name, email, role, subscription, trial dates)

ADMIN USER MANAGEMENT ROUTES
-----------------------------
1. GET /users/
   - Purpose: List all users (paginated)
   - Middleware: token_required + require_role("admin")
   - Query Params: page (default 1), per_page (default 20)
   - Response: Paginated list of users

2. POST /users/<user_id>/status
   - Purpose: Set user active/inactive
   - Middleware: token_required + require_role("admin")
   - Body: { "is_active": true/false }
   - Response: { "message": "User <id> active status set to <true/false>" }

3. DELETE /users/<user_id>
   - Purpose: Delete a user
   - Middleware: token_required + require_role("admin")
   - Response: { "message": "User <id> deleted successfully" }

GYM OWNER ENROLLMENT MANAGEMENT ROUTES
--------------------------------------
1. POST /enrollments/gym/<gym_id>/user/<user_id>/status
   - Purpose: Activate or deactivate a user's enrollment in a gym
   - Middleware: token_required + require_role("gym_owner")
   - Body: { "is_active": true/false }
   - Response: { "message": "User <id> enrollment set to <true/false>" }

2. GET /enrollments/gym/<gym_id>/members
   - Purpose: Get paginated list of members for a gym
   - Middleware: token_required + require_role("gym_owner")
   - Query Params: page (default 1), per_page (default 20)
   - Response:
     {
       "members": [
         {
           "id": <user_id>,
           "name": "User Name",
           "email": "user@example.com",
           "phone": "1234567890",
           "enrolled_at": "2025-11-26T05:00:00Z",
           "valid_till": "2025-12-26T05:00:00Z",
           "is_active": true
         }
       ],
       "total": <total_members>,
       "total_pages": <total_pages>,
       "page": <current_page>,
       "per_page": <per_page>
     }

3. POST /enrollments/gym/<gym_id>/user/<user_id>/unenroll
   - Purpose: Unenroll a user from a gym
   - Middleware: token_required + require_role("gym_owner")
   - Response: { "message": "User <id> unenrolled from gym <id>" }

PAGINATION PARAMETERS (Optional for list endpoints)
---------------------------------------------------
- page: integer (default 1)
- per_page: integer (default 20)

EXAMPLES:
GET /enrollments/gym/1/members?page=2&per_page=50
POST /enrollments/gym/1/user/10/status
POST /enrollments/gym/1/user/10/unenroll
"""
