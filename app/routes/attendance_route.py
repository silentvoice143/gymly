from flask_restx import Namespace, Resource, fields
from flask import request, make_response
from app.services.attendance_service import AttendanceService
from app.middleware.auth_middleware import token_required
from app.middleware.role_middleware import require_role
from datetime import datetime

attendance_ns = Namespace("Attendance", description="User attendance APIs")

# ------------------ MODELS ------------------
attendance_model = attendance_ns.model("AttendanceModel", {
    "gym_id": fields.Integer(required=True)
})

# ------------------ USER ROUTES ------------------
@attendance_ns.route("/record")
class RecordAttendanceAPI(Resource):
    @token_required
    @require_role("user")
    @attendance_ns.expect(attendance_model)
    def post(self):
        """Record user's attendance for today"""
        data = request.get_json()
        user = getattr(request, "current_user")
        gym_id = data.get("gym_id")
        result, error = AttendanceService.record_attendance(user.id, gym_id)
        if error:
            return {"error": error}, 400
        return result, 200


@attendance_ns.route("/my-attendance")
class MyAttendanceAPI(Resource):
    @token_required
    @require_role("user")
    def get(self):
        """Get paginated attendance records for the current user"""
        user = getattr(request, "current_user")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        result, error = AttendanceService.get_attendance(user.id, page, per_page)
        if error:
            return {"error": error}, 400
        return result, 200


# ------------------ GYM OWNER ROUTES ------------------
@attendance_ns.route("/gym/<int:gym_id>/attendance")
class GymAttendanceAPI(Resource):
    @token_required
    @require_role("gym_owner")
    def get(self, gym_id):
        """
        Get all attendance for a gym (paginated)
        Optional query params:
        - page: page number
        - per_page: items per page
        - user_id: filter by a specific user
        - start_date: filter from this date (YYYY-MM-DD)
        - end_date: filter until this date (YYYY-MM-DD)
        """
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        user_id = request.args.get("user_id", type=int)
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        fmt = "%Y-%m-%d"
        if start_date:
            start_date = datetime.strptime(start_date, fmt)
        if end_date:
            end_date = datetime.strptime(end_date, fmt)

        result, error = AttendanceService.get_gym_attendance(
            gym_id, page, per_page, user_id, start_date, end_date
        )
        if error:
            return {"error": error}, 404
        return result, 200


@attendance_ns.route("/gym/<int:gym_id>/attendance/pdf")
class GymAttendancePDFAPI(Resource):
    @token_required
    @require_role("gym_owner")
    def get(self, gym_id):
        """
        Generate a PDF report of gym attendance.
        Optional query params:
        - user_id: filter by a specific user
        - start_date: filter from this date (YYYY-MM-DD)
        - end_date: filter until this date (YYYY-MM-DD)
        """
        user_id = request.args.get("user_id", type=int)
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        fmt = "%Y-%m-%d"
        if start_date:
            start_date = datetime.strptime(start_date, fmt)
        if end_date:
            end_date = datetime.strptime(end_date, fmt)

        pdf_data, error = AttendanceService.generate_pdf(gym_id, user_id, start_date, end_date)
        if error:
            return {"error": error}, 404

        # Return PDF as downloadable file
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=gym_{gym_id}_attendance.pdf'
        return response, 200

# ------------------ COMMENTS ------------------
"""
User Routes:
- POST /attendance/record → Record attendance for today
- GET  /attendance/my-attendance → Paginated attendance records for current user

Gym Owner Routes:
- GET  /attendance/gym/<gym_id>/attendance → Get paginated attendance for gym (filters: user_id, start_date, end_date)
- GET  /attendance/gym/<gym_id>/attendance/pdf → Download attendance report as PDF (filters: user_id, start_date, end_date)
"""
