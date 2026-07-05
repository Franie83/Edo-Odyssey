from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from ..models.models import News, NewsComment
from ..extensions import db

news_bp = Blueprint("news", __name__, url_prefix="/news")


@news_bp.route("/")
def list_news():
    page = request.args.get("page", 1, type=int)
    search_q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    query = News.query.filter_by(status="active")
    if search_q:
        query = query.filter(News.title.ilike(f"%{search_q}%"))
    if category:
        query = query.filter_by(category=category)
    query = query.order_by(News.created_at.desc())

    pagination = query.paginate(page=page, per_page=9, error_out=False)
    featured = News.query.filter_by(featured=True, status="active").limit(3).all()
    categories = [r.category for r in News.query.with_entities(News.category).distinct().all()]
    return render_template(
        "news/list.html",
        articles=pagination.items,
        pagination=pagination,
        featured=featured,
        categories=categories,
        search_q=search_q,
        selected_category=category,
    )


@news_bp.route("/<int:id>")
def detail(id):
    article = News.query.filter_by(id=id, status="active").first_or_404()
    article.views = (article.views or 0) + 1
    db.session.commit()
    comments = NewsComment.query.filter_by(news_id=id).order_by(NewsComment.created_at.desc()).all()
    related = News.query.filter(News.category == article.category, News.id != id, News.status == "active").limit(3).all()
    return render_template("news/detail.html", article=article, comments=comments, related=related)


@news_bp.route("/<int:id>/comment", methods=["POST"])
@login_required
def add_comment(id):
    article = News.query.get_or_404(id)
    comment_text = request.form.get("comment", "").strip()
    if not comment_text:
        flash("Comment cannot be empty.", "warning")
        return redirect(url_for("news.detail", id=id))
    c = NewsComment(news_id=id, user_id=current_user.id, comment=comment_text)
    db.session.add(c)
    db.session.commit()
    flash("Comment posted!", "success")
    return redirect(url_for("news.detail", id=id))
