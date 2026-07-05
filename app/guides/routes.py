from flask import Blueprint, render_template, request
from ..models.models import Guide, Review

guides_bp = Blueprint("guides", __name__, url_prefix="/guides")


@guides_bp.route("/")
def list_guides():
    page = request.args.get("page", 1, type=int)
    search_q = request.args.get("q", "").strip()
    lang = request.args.get("language", "").strip()
    sort = request.args.get("sort", "experience")

    query = Guide.query.filter_by(verification_status="Approved", status="active")
    if search_q:
        from ..models.models import User
        query = query.join(User).filter(
            (User.first_name.ilike(f"%{search_q}%")) | (User.last_name.ilike(f"%{search_q}%"))
        )
    if lang:
        query = query.filter(Guide.languages.ilike(f"%{lang}%"))
    if sort == "rate_asc":
        query = query.order_by(Guide.hourly_rate.asc())
    elif sort == "rate_desc":
        query = query.order_by(Guide.hourly_rate.desc())
    else:
        query = query.order_by(Guide.experience.desc())

    pagination = query.paginate(page=page, per_page=9, error_out=False)
    return render_template(
        "guides/list.html",
        guides=pagination.items,
        pagination=pagination,
        search_q=search_q,
        selected_lang=lang,
        sort=sort,
    )


@guides_bp.route("/<int:id>")
def detail(id):
    guide = Guide.query.filter_by(id=id, verification_status="Approved").first_or_404()
    reviews = Review.query.filter_by(target_type="Guide", target_id=id, is_approved=True).order_by(Review.created_at.desc()).all()
    return render_template("guides/detail.html", guide=guide, reviews=reviews)
