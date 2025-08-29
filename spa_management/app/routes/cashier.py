from flask import Blueprint, render_template, session, redirect, url_for
from ..models import Cashier
from ..utils.auth_helpers import get_current_cashier

cashier_bp = Blueprint("cashier", __name__)


@cashier_bp.get("/cashier")
def cashier_page():
    # Use hybrid authentication (token-first, session fallback)
    cashier, auth_method = get_current_cashier()
    
    if not cashier:
        return redirect(url_for("auth.login_cashier_form"))
    
    return render_template("cashier.html", 
                         cashier_name=cashier.name, 
                         counter_number=cashier.counter_number)


@cashier_bp.get("/cashier/payment-management")
def payment_management_page():
    # Use hybrid authentication (token-first, session fallback)
    cashier, auth_method = get_current_cashier()
    
    if not cashier:
        return redirect(url_for("auth.login_cashier_form"))
    
    return render_template("payment_management.html", 
                         cashier_name=cashier.name, 
                         counter_number=cashier.counter_number)
