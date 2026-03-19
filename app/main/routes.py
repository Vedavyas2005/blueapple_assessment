from datetime import date, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Slot, Booking
import uuid

main_bp = Blueprint("main", __name__)

PURPOSES = ["Team Meeting", "Client Call", "Interview", "Training", "Demo", "Other"]


def generate_reference():
    today = date.today().strftime("%Y%m%d")
    short = uuid.uuid4().hex[:6].upper()
    return f"BA-{today}-{short}"


@main_bp.route("/")
@login_required
def index():
    today = date.today()
    # Show next 7 days
    dates = [today + timedelta(days=i) for i in range(7)]
    selected_date_str = request.args.get("date", today.isoformat())

    try:
        selected_date = date.fromisoformat(selected_date_str)
    except ValueError:
        selected_date = today

    slots = (
        Slot.query.filter_by(date=selected_date, is_active=True)
        .order_by(Slot.start_time)
        .all()
    )

    # Stats
    total_available = sum(1 for s in slots if s.is_available)
    total_booked = sum(1 for s in slots if not s.is_available)

    # User's upcoming bookings
    my_bookings = (
        Booking.query.filter(
            Booking.user_id == current_user.id,
            Booking.status != "cancelled",
        )
        .join(Slot)
        .filter(Slot.date >= today)
        .order_by(Slot.date, Slot.start_time)
        .limit(5)
        .all()
    )

    return render_template(
        "main/index.html",
        dates=dates,
        selected_date=selected_date,
        slots=slots,
        purposes=PURPOSES,
        total_available=total_available,
        total_booked=total_booked,
        my_bookings=my_bookings,
    )


@main_bp.route("/book/<int:slot_id>", methods=["POST"])
@login_required
def book(slot_id):
    slot = Slot.query.get_or_404(slot_id)

    if not slot.is_available:
        flash("This slot is no longer available.", "danger")
        return redirect(url_for("main.index", date=slot.date.isoformat()))

    # Check if user already booked this slot
    existing = Booking.query.filter_by(
        user_id=current_user.id, slot_id=slot_id, status="confirmed"
    ).first()
    if existing:
        flash("You already have a booking for this slot.", "warning")
        return redirect(url_for("main.index", date=slot.date.isoformat()))

    purpose = request.form.get("purpose", "Other")
    notes = request.form.get("notes", "").strip()

    booking = Booking(
        reference=generate_reference(),
        user_id=current_user.id,
        slot_id=slot_id,
        purpose=purpose,
        notes=notes if notes else None,
        status="confirmed",
    )
    db.session.add(booking)
    db.session.commit()

    flash(
        f"Booking confirmed! Your reference is {booking.reference}.",
        "success",
    )
    return redirect(url_for("main.my_bookings"))


@main_bp.route("/my-bookings")
@login_required
def my_bookings():
    today = date.today()
    bookings = (
        Booking.query.filter_by(user_id=current_user.id)
        .join(Slot)
        .order_by(Slot.date.desc(), Slot.start_time.desc())
        .all()
    )
    return render_template("main/my_bookings.html", bookings=bookings, today=today)


@main_bp.route("/cancel/<int:booking_id>", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        flash("You are not authorised to cancel this booking.", "danger")
        return redirect(url_for("main.my_bookings"))

    if booking.status == "cancelled":
        flash("This booking is already cancelled.", "warning")
        return redirect(url_for("main.my_bookings"))

    booking.status = "cancelled"
    db.session.commit()
    flash(f"Booking {booking.reference} has been cancelled.", "info")
    return redirect(url_for("main.my_bookings"))