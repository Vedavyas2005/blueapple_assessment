import re
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User
from app.config import Config

auth_bp = Blueprint("auth", __name__)


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        phone = request.form.get("phone", "").strip()
        admin_secret = request.form.get("admin_secret", "").strip()

        # Basic validation
        if not name or not email or not password:
            flash("Name, email, and password are required.", "danger")
            return redirect(url_for("auth.register"))

        if not is_valid_email(email):
            flash("Invalid email address.", "danger")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "danger")
            return redirect(url_for("auth.register"))

        is_admin = admin_secret == Config.ADMIN_SECRET

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            phone=phone if phone else None,
            is_admin=is_admin,
        )
        db.session.add(user)
        db.session.commit()

        if is_admin:
            flash(f"Admin account created for {name}. You can now log in.", "success")
        else:
            flash(f"Account created for {name}. You can now log in.", "success")

        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user, remember=remember)
        flash(f"Welcome back, {user.name}!", "success")

        next_page = request.args.get("next")
        if next_page and next_page.startswith("/"):
            return redirect(next_page)

        if user.is_admin:
            return redirect(url_for("admin.dashboard"))

        return redirect(url_for("main.index"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))