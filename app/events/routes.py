from flask import Blueprint, render_template, request
from ..models.models import Event
from datetime import datetime

events_bp = Blueprint("events", __name__, url_prefix="/events")


@events_bp.route("/")
def list_events():
    page = request.args.get("page", 1, type=int)
    search_q = request.args.get("q", "").strip()
    filter_type = request.args.get("filter", "upcoming")

    query = Event.query.filter_by(active=True, status="active")
    if search_q:
        query = query.filter(Event.name.ilike(f"%{search_q}%"))
    if filter_type == "upcoming":
        query = query.filter(Event.date >= datetime.utcnow())
    elif filter_type == "past":
        query = query.filter(Event.date < datetime.utcnow())
    query = query.order_by(Event.date.asc())

    pagination = query.paginate(page=page, per_page=9, error_out=False)
    return render_template(
        "events/list.html",
        events=pagination.items,
        pagination=pagination,
        search_q=search_q,
        filter_type=filter_type,
        now=datetime.utcnow(),
    )


@events_bp.route("/<int:id>")
def detail(id):
    event = Event.query.filter_by(id=id, active=True).first_or_404()
    return render_template("events/detail.html", event=event, now=datetime.utcnow())
