from flask import Blueprint, redirect, url_for
from ..models.models import QRCode, Attraction
from ..extensions import db
from datetime import datetime

qr_bp = Blueprint("qr", __name__, url_prefix="/qr")


@qr_bp.route("/scan/<int:attraction_id>")
def scan(attraction_id):
    """Handle QR code scan — redirect to attraction and record scan."""
    attraction = Attraction.query.get_or_404(attraction_id)
    qr = QRCode.query.filter_by(attraction_id=attraction_id).first()
    if qr:
        qr.scanned_count = (qr.scanned_count or 0) + 1
        qr.last_scanned = datetime.utcnow()
        db.session.commit()
    return redirect(url_for("attractions.detail", id=attraction_id))
