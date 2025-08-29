from flask import Blueprint, render_template, session, redirect, url_for
from ..models import Therapist
from ..utils.auth_helpers import get_current_therapist

therapist_bp = Blueprint("therapist", __name__)


@therapist_bp.get("/therapist")
def therapist_page():
    # Use hybrid authentication (token-first, session fallback)
    therapist, auth_method = get_current_therapist()
    
    if not therapist:
        return redirect(url_for("auth.login_therapist_form"))
    
    return render_template("therapist.html", 
                         therapist_name=therapist.name, 
                         room_number=therapist.room_number)


@therapist_bp.get("/therapist/service-management")
def service_management_page():
    # Use hybrid authentication (token-first, session fallback)
    therapist, auth_method = get_current_therapist()
    
    if not therapist:
        return redirect(url_for("auth.login_therapist_form"))
    
    return render_template("service_management.html", 
                         therapist_name=therapist.name, 
                         room_number=therapist.room_number)
