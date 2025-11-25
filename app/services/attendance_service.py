from flask import request
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
from app.extensions import db
from app.models.attendance import Attendance
from app.models.user import User
from app.models.gym import Gym
from app.models.gym_enrollment import GymEnrollment

def paginate_query(query, page=1, per_page=20):
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


class AttendanceService:

    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, "Gym Attendance Report", 0, 1, "C")
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    # ------------------- RECORD ATTENDANCE -------------------
    @staticmethod
    def record_attendance(user_id, gym_id):
        user = User.query.get(user_id)
        if not user:
            return None, "User not found"

        gym = Gym.query.get(gym_id)
        if not gym:
            return None, "Gym not found"

        enrollment = GymEnrollment.query.filter_by(
            user_id=user_id, gym_id=gym_id, is_active=True
        ).first()
        if not enrollment:
            return None, "User not enrolled or inactive"

        today = datetime.utcnow().date()
        existing = Attendance.query.filter(
            Attendance.user_id == user_id,
            Attendance.gym_id == gym_id,
            db.func.date(Attendance.timestamp) == today
        ).first()

        if existing:
            return None, "Attendance already recorded today"

        attendance = Attendance(user_id=user_id, gym_id=gym_id, timestamp=datetime.utcnow())
        db.session.add(attendance)
        db.session.commit()
        return {"message": f"{user.name} attendance recorded at {gym.name}"}, None

    # ------------------- GET USER ATTENDANCE -------------------
    @staticmethod
    def get_attendance(user_id, page=1, per_page=20):
        query = Attendance.query.filter_by(user_id=user_id).order_by(Attendance.timestamp.desc())
        pagination = paginate_query(query, page, per_page)

        records = [
            {
                "id": a.id,
                "gym_id": a.gym_id,
                "gym_name": a.gym.name if a.gym else None,
                "timestamp": a.timestamp.isoformat()
            } for a in pagination["items"]
        ]
        return {
            "records": records,
            "total": pagination["total"],
            "total_pages": pagination["total_pages"],
            "page": pagination["page"],
            "per_page": pagination["per_page"]
        }, None

    # ------------------- GET GYM ATTENDANCE -------------------
    @staticmethod
    def get_gym_attendance(gym_id, page=1, per_page=20, user_id=None, start_date=None, end_date=None):
        gym = Gym.query.get(gym_id)
        if not gym:
            return None, "Gym not found"

        query = Attendance.query.filter_by(gym_id=gym_id)
        if user_id:
            query = query.filter(Attendance.user_id == user_id)
        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Attendance.timestamp >= start_date)
        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(Attendance.timestamp <= end_date)

        query = query.order_by(Attendance.timestamp.desc())
        pagination = paginate_query(query, page, per_page)

        records = [
            {
                "id": a.id,
                "user_id": a.user.id if a.user else None,
                "user_name": a.user.name if a.user else None,
                "timestamp": a.timestamp.isoformat()
            } for a in pagination["items"]
        ]

        return {
            "records": records,
            "total": pagination["total"],
            "total_pages": pagination["total_pages"],
            "page": pagination["page"],
            "per_page": pagination["per_page"]
        }, None

    # ------------------- GENERATE PDF -------------------
    @staticmethod
    def generate_pdf(gym_id, user_id=None, start_date=None, end_date=None):
      gym = Gym.query.get(gym_id)
      if not gym:
        return None, "Gym not found"

      query = Attendance.query.filter_by(gym_id=gym_id)

      if user_id:
        query = query.filter(Attendance.user_id == user_id)
      if start_date:
        query = query.filter(Attendance.timestamp >= start_date)
      if end_date:
        query = query.filter(Attendance.timestamp <= end_date)

      query = query.order_by(Attendance.timestamp.desc())
      records = query.all()

      if not records:
        return None, "No attendance records found for the selected filters"

      pdf = AttendanceService.PDF()
      pdf.add_page()
      pdf.set_font("Arial", "B", 12)
      pdf.cell(0, 10, f"Gym: {gym.name} Attendance Report", 0, 1, "C")
      pdf.ln(5)

    # Table header
      pdf.set_font("Arial", "B", 10)
      pdf.cell(20, 10, "ID", 1)
      pdf.cell(50, 10, "User Name", 1)
      pdf.cell(50, 10, "Email", 1)
      pdf.cell(40, 10, "Date & Time", 1)
      pdf.ln()

      pdf.set_font("Arial", "", 10)
      for a in records:
        pdf.cell(20, 10, str(a.id), 1)
        pdf.cell(50, 10, a.user.name if a.user else "-", 1)
        pdf.cell(50, 10, a.user.email if a.user else "-", 1)
        pdf.cell(40, 10, a.timestamp.strftime("%Y-%m-%d %H:%M"), 1)
        pdf.ln()

      return pdf.output(dest="S").encode("latin1"), None