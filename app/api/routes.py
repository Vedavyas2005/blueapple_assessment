from datetime import date
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Slot, Booking

api_bp = Blueprint("api", __name__)


@api_bp.route("/slots")
@login_required
def slots():
    date_str = request.args.get("date", date.today().isoformat())
    try:
        selected_date = date.fromisoformat(date_str)
    except ValueError:
        return jsonify({"error": "Invalid date"}), 400

    slots = (
        Slot.query.filter_by(date=selected_date, is_active=True)
        .order_by(Slot.start_time)
        .all()
    )

    return jsonify(
        [
            {
                "id": s.id,
                "start_time": s.start_time.strftime("%I:%M %p"),
                "end_time": s.end_time.strftime("%I:%M %p"),
                "available": s.is_available,
                "booked_count": s.booked_count,
                "capacity": s.capacity,
            }
            for s in slots
        ]
    )


@api_bp.route("/my-bookings")
@login_required
def my_bookings_json():
    bookings = Booking.query.filter_by(
        user_id=current_user.id
    ).join(Slot).order_by(Slot.date.desc()).limit(20).all()

    return jsonify(
        [
            {
                "id": b.id,
                "reference": b.reference,
                "date": b.slot.date.isoformat(),
                "start_time": b.slot.start_time.strftime("%I:%M %p"),
                "purpose": b.purpose,
                "status": b.status,
            }
            for b in bookings
        ]
    )