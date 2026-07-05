from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from ..extensions import db
from ..models.models import User, AuditLog
from ..utils.helpers import log_action

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html")

        if user.status == "deleted":
            flash("Your account has been deactivated. Contact EDSTA support.", "danger")
            return render_template("auth/login.html")

        from datetime import datetime
        user.last_login = datetime.utcnow()
        db.session.commit()

        login_user(user, remember=remember)
        log_action(f"User logged in via browser portal", module="auth")

        next_page = request.args.get("next")
        flash(f"Welcome back, {user.first_name}! 🎉", "success")
        if next_page:
            return redirect(next_page)
        if user.is_admin:
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        phone = request.form.get("phone", "").strip()

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("auth/register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("auth/register.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for("auth.login"))

        # 🔒 FIX: Force all new registrations to be "Tourist"
        # Only admins can promote users to Guide, Hotel, Restaurant, or Admin roles
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role="Tourist",  # Always Tourist on registration
            phone=phone,
            is_verified=False,  # Needs admin verification
            status="active",
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        log_action(f"New user registered: {email} as Tourist", module="auth")
        flash(f"Account created successfully! Welcome to Edo Odyssey, {first_name}!", "success")
        login_user(user)
        return redirect(url_for("dashboard.index"))

    return render_template("auth/register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    log_action("User logged out", module="auth")
    logout_user()
    flash("You have been logged out safely.", "info")
    return redirect(url_for("main.home"))


@auth_bp.route("/quick-login/<role>")
def quick_login(role):
    """Quick access login for demos."""
    role_map = {
        "superadmin": "superadmin@edo.gov.ng",
        "admin": "admin@edo.gov.ng",
        "tourist": "tourist@gmail.com",
        "guide": "guide@edo.gov.ng",
        "hotel": "hotel@emotan.com",
        "restaurant": "restaurant@mamaebo.com",  # Restaurant owner
    }
    email = role_map.get(role.lower())
    if not email:
        flash("Invalid quick login role.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Demo user not found. Ensure database is seeded.", "danger")
        return redirect(url_for("auth.login"))

    logout_user()
    login_user(user, remember=True)
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.session.commit()
    log_action(f"Quick demo login as {role}", module="auth")
    flash(f"Logged in as {user.full_name} ({user.role})", "success")
    if user.is_admin:
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("dashboard.index"))