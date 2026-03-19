from datetime import date, time, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Slot, Booking, User

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    today = date.today()

    total_users = User.query.count()
    total_slots = Slot.query.filter_by(is_active=True).count()
    total_bookings = Booking.query.filter(Booking.status != "cancelled").count()
    today_bookings = (
        Booking.query.join(Slot)
        .filter(Slot.date == today, Booking.status != "cancelled")
        .count()
    )

    recent_bookings = (
        Booking.query.join(Slot)
        .order_by(Booking.created_at.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_slots=total_slots,
        total_bookings=total_bookings,
        today_bookings=today_bookings,
        recent_bookings=recent_bookings,
        today=today,
    )


@admin_bp.route("/slots")
@login_required
@admin_required
def manage_slots():
    today = date.today()
    slots = (
        Slot.query.filter(Slot.date >= today)
        .order_by(Slot.date, Slot.start_time)
        .all()
    )
    return render_template("admin/slots.html", slots=slots, today=today)


@admin_bp.route("/slots/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_slot():
    if request.method == "POST":
        date_str = request.form.get("date", "")
        start_str = request.form.get("start_time", "")
        end_str = request.form.get("end_time", "")
        capacity = request.form.get("capacity", "1")
        bulk = request.form.get("bulk") == "on"
        bulk_days = request.form.get("bulk_days", "1")

        try:
            slot_date = date.fromisoformat(date_str)
            start = time.fromisoformat(start_str)
            end = time.fromisoformat(end_str)
            capacity = int(capacity)
            bulk_days = int(bulk_days) if bulk else 1
        except ValueError:
            flash("Invalid date or time values.", "danger")
            return redirect(url_for("admin.add_slot"))

        if start >= end:
            flash("Start time must be before end time.", "danger")
            return redirect(url_for("admin.add_slot"))

        added = 0
        for i in range(bulk_days):
            d = slot_date + timedelta(days=i)
            # Avoid duplicate slots
            exists = Slot.query.filter_by(date=d, start_time=start).first()
            if not exists:
                s = Slot(date=d, start_time=start, end_time=end, capacity=capacity)
                db.session.add(s)
                added += 1

        db.session.commit()
        flash(f"{added} slot(s) added successfully.", "success")
        return redirect(url_for("admin.manage_slots"))

    return render_template("admin/add_slot.html")


@admin_bp.route("/slots/toggle/<int:slot_id>", methods=["POST"])
@login_required
@admin_required
def toggle_slot(slot_id):
    slot = Slot.query.get_or_404(slot_id)
    slot.is_active = not slot.is_active
    db.session.commit()
    status = "activated" if slot.is_active else "deactivated"
    flash(f"Slot {status}.", "info")
    return redirect(url_for("admin.manage_slots"))


@admin_bp.route("/slots/delete/<int:slot_id>", methods=["POST"])
@login_required
@admin_required
def delete_slot(slot_id):
    slot = Slot.query.get_or_404(slot_id)
    Booking.query.filter_by(slot_id=slot_id).delete()
    db.session.delete(slot)
    db.session.commit()
    flash("Slot and its bookings deleted.", "danger")
    return redirect(url_for("admin.manage_slots"))


@admin_bp.route("/bookings")
@login_required
@admin_required
def manage_bookings():
    status_filter = request.args.get("status", "all")
    query = Booking.query.join(Slot).order_by(Slot.date.desc(), Slot.start_time)

    if status_filter != "all":
        query = query.filter(Booking.status == status_filter)

    bookings = query.all()
    return render_template(
        "admin/bookings.html", bookings=bookings, status_filter=status_filter
    )


@admin_bp.route("/bookings/update/<int:booking_id>", methods=["POST"])
@login_required
@admin_required
def update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    new_status = request.form.get("status")
    if new_status in ("confirmed", "pending", "cancelled"):
        booking.status = new_status
        db.session.commit()
        flash(f"Booking {booking.reference} status updated to {new_status}.", "success")
    return redirect(url_for("admin.manage_bookings"))


@admin_bp.route("/users")
@login_required
@admin_required
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)