from flask import Blueprint, render_template
from ..models import Transaction

monitor_bp = Blueprint("monitor", __name__)


@monitor_bp.get("/monitor/")
def monitor_page():
    return render_template("monitor.html")


@monitor_bp.get("/receipt/<code>")
def receipt_page(code: str):
    tx = Transaction.query.filter_by(code=code).first()
    return render_template("receipt.html", tx=tx)
