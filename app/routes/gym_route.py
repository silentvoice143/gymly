from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.gym_service import GymService
from app.middleware.auth_middleware import token_required
from app.middleware.role_middleware import require_role
from app.middleware.subscription_middleware import subscription_required

gym_ns = Namespace("Gyms", description="Gym management APIs")

# ------------------ MODELS ------------------
gym_model = gym_ns.model("GymModel", {
    "name": fields.String(required=True),
    "location": fields.String(required=True)
})

enroll_model = gym_ns.model("EnrollModel", {
    "gym_id": fields.Integer(required=True)
})

# ------------------ PUBLIC ROUTES ------------------
@gym_ns.route("/all")
class AllGymsAPI(Resource):
    def get(self):
        """Get all gyms (public) with pagination"""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        gyms = GymService.get_all_gyms(page, per_page)
        return gyms, 200

@gym_ns.route("/<int:gym_id>")
class GymDetailAPI(Resource):
    def get(self, gym_id):
        """Get gym details by ID"""
        gym, error = GymService.get_gym_by_id(gym_id)
        if error:
            return {"error": error}, 404
        return gym, 200

# ------------------ GYM OWNER ROUTES ------------------
@gym_ns.route("/")
class GymListAPI(Resource):
    @token_required
    @require_role("gym_owner")
    @subscription_required
    @gym_ns.expect(gym_model)
    def post(self):
        """Create a new gym (Owner only, subscription required)"""
        data = request.get_json()
        gym, error = GymService.create_gym(data)
        if error:
            return {"error": error}, 400
        return {"message": "Gym created", "gym_id": gym.id}, 201

    @token_required
    @require_role("gym_owner")
    @subscription_required
    def get(self):
        """Get all gyms owned by the current owner with pagination"""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        owner = getattr(request, "current_user")
        query = Gym.query.filter_by(owner_id=owner.id)
        gyms = GymService.get_all_gyms(page, per_page)  # We can reuse the same pagination
        return gyms, 200

@gym_ns.route("/<int:gym_id>/members")
class GymMembersAPI(Resource):
    @token_required
    @require_role("gym_owner")
    @subscription_required
    def get(self, gym_id):
        """Get all members enrolled in a gym with pagination"""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        members, error = GymService.get_gym_members(gym_id, page, per_page)
        if error:
            return {"error": error}, 400
        return members, 200

@gym_ns.route("/<int:gym_id>")
class GymModifyAPI(Resource):
    @token_required
    @require_role("gym_owner")
    @subscription_required
    @gym_ns.expect(gym_model)
    def put(self, gym_id):
        """Update a gym (Owner only)"""
        data = request.get_json()
        gym, error = GymService.update_gym(gym_id, data)
        if error:
            return {"error": error}, 400
        return {"message": "Gym updated successfully"}, 200

    @token_required
    @require_role("gym_owner")
    @subscription_required
    def delete(self, gym_id):
        """Delete a gym (Owner only)"""
        response, error = GymService.delete_gym(gym_id)
        if error:
            return {"error": error}, 400
        return response, 200

# ------------------ USER ROUTES ------------------
@gym_ns.route("/enroll")
class EnrollGymAPI(Resource):
    @token_required
    @require_role("user")
    @gym_ns.expect(enroll_model)
    def post(self):
        """Enroll current user into a gym"""
        data = request.get_json()
        response, error = GymService.enroll_at_gym(data)
        if error:
            return {"error": error}, 400
        return response, 200

@gym_ns.route("/unenroll")
class UnenrollGymAPI(Resource):
    @token_required
    @require_role("user")
    @gym_ns.expect(enroll_model)
    def post(self):
        """Unenroll current user from a gym"""
        data = request.get_json()
        response, error = GymService.unenroll_from_gym(data)
        if error:
            return {"error": error}, 400
        return response, 200

@gym_ns.route("/my-gyms")
class MyGymsAPI(Resource):
    @token_required
    @require_role("user")
    def get(self):
        """Get all gyms the current user is enrolled in with pagination"""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        gyms, error = GymService.get_my_gyms(page, per_page)
        if error:
            return {"error": error}, 400
        return gyms, 200
"""
==========================
GYM & USER API REFERENCE
==========================

PUBLIC GYM ROUTES (No authentication required)
------------------------------------------------
1. GET /gyms/all
   - Purpose: List all gyms
   - Pagination: page, per_page (optional)
   - Response: Paginated list of gyms with id, name, location, owner info

2. GET /gyms/<gym_id>
   - Purpose: Get details of a single gym by ID
   - Response: Gym info: id, name, location, owner_id, owner_name

GYM OWNER ROUTES (Authentication + Subscription required)
---------------------------------------------------------
Middleware:
- token_required (auth)
- require_role("gym_owner") (role check)
- subscription_required (active subscription check)

1. POST /gyms/
   - Purpose: Create a new gym
   - Body: { "name": "Gym Name", "location": "Location" }
   - Response: { "message": "Gym created", "gym_id": <id> }

2. GET /gyms/
   - Purpose: List gyms owned by current owner
   - Pagination: page, per_page (optional)
   - Response: Paginated list of gyms

3. PUT /gyms/<gym_id>
   - Purpose: Update gym details
   - Body: { "name": "New Name", "location": "New Location" }
   - Response: { "message": "Gym updated successfully" }

4. DELETE /gyms/<gym_id>
   - Purpose: Delete a gym
   - Response: { "message": "Gym deleted successfully" }

5. GET /gyms/<gym_id>/members
   - Purpose: List members enrolled in a gym
   - Pagination: page, per_page (optional)
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

USER ROUTES (Authentication required)
-------------------------------------
Middleware:
- token_required
- require_role("user")

1. POST /gyms/enroll
   - Purpose: Enroll current user into a gym
   - Body: { "gym_id": 1 }
   - Response: { "message": "User <name> enrolled in gym <gym_name>" }

2. POST /gyms/unenroll
   - Purpose: Unenroll current user from a gym
   - Body: { "gym_id": 1 }
   - Response: { "message": "User <name> unenrolled from gym <gym_name>" }

3. GET /gyms/my-gyms
   - Purpose: List all gyms the current user is enrolled in
   - Pagination: page, per_page (optional)
   - Response:
     {
       "gyms": [
         {
           "id": 1,
           "name": "Power Gym",
           "location": "New York",
           "owner_id": 2,
           "owner_name": "Alice",
           "enrolled_at": "2025-11-26T05:00:00Z",
           "valid_till": "2025-12-26T05:00:00Z",
           "is_active": true
         }
       ],
       "total": 20,
       "total_pages": 2,
       "page": 1,
       "per_page": 10
     }

PAGINATION PARAMETERS (Optional for all list endpoints)
-------------------------------------------------------
- page: integer (default 1)
- per_page: integer (default 20)

EXAMPLE:
GET /gyms/all?page=2&per_page=10
GET /gyms/123/members?page=1&per_page=50
GET /gyms/my-gyms?page=1&per_page=10
"""
