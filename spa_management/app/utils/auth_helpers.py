"""Authentication helper functions for token-based auth"""
from datetime import datetime, timedelta
from functools import wraps
import secrets
from typing import Optional, Union, Tuple

from flask import request, jsonify, session
from ..models import Therapist, Cashier
from ..extensions import db


def generate_auth_token() -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)


def create_token_for_user(user: Union[Therapist, Cashier]) -> str:
    """Create and save auth token for a user"""
    token = generate_auth_token()
    user.auth_token = token
    user.token_expires_at = datetime.now() + timedelta(hours=24)  # Token valid for 24 hours
    db.session.commit()
    return token


def invalidate_token(user: Union[Therapist, Cashier]) -> None:
    """Invalidate a user's auth token"""
    user.auth_token = None
    user.token_expires_at = None
    db.session.commit()


def get_token_from_request() -> Optional[str]:
    """Extract token from request headers or query parameters"""
    # Check Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    
    # Check X-Auth-Token header
    token = request.headers.get('X-Auth-Token')
    if token:
        return token
    
    # Check query parameter (for websocket connections)
    token = request.args.get('auth_token')
    if token:
        return token
    
    return None


def validate_therapist_token(token: str) -> Optional[Therapist]:
    """Validate therapist auth token"""
    if not token:
        return None
    
    therapist = Therapist.query.filter_by(auth_token=token).first()
    if not therapist:
        return None
    
    # Check if token is expired
    if therapist.token_expires_at and therapist.token_expires_at < datetime.now():
        invalidate_token(therapist)
        return None
    
    # Extend token expiration on successful validation
    therapist.token_expires_at = datetime.now() + timedelta(hours=24)
    db.session.commit()
    
    return therapist


def validate_cashier_token(token: str) -> Optional[Cashier]:
    """Validate cashier auth token"""
    if not token:
        return None
    
    cashier = Cashier.query.filter_by(auth_token=token).first()
    if not cashier:
        return None
    
    # Check if token is expired
    if cashier.token_expires_at and cashier.token_expires_at < datetime.now():
        invalidate_token(cashier)
        return None
    
    # Extend token expiration on successful validation
    cashier.token_expires_at = datetime.now() + timedelta(hours=24)
    db.session.commit()
    
    return cashier


def get_current_therapist() -> Tuple[Optional[Therapist], Optional[str]]:
    """Get current therapist from token or session"""
    # Try token first
    token = get_token_from_request()
    if token:
        therapist = validate_therapist_token(token)
        if therapist:
            return therapist, 'token'
    
    # Fallback to session
    therapist_id = session.get('therapist_id')
    if therapist_id:
        therapist = Therapist.query.get(therapist_id)
        if therapist:
            return therapist, 'session'
    
    return None, None


def get_current_cashier() -> Tuple[Optional[Cashier], Optional[str]]:
    """Get current cashier from token or session"""
    # Try token first
    token = get_token_from_request()
    if token:
        cashier = validate_cashier_token(token)
        if cashier:
            return cashier, 'token'
    
    # Fallback to session
    cashier_id = session.get('cashier_id')
    if cashier_id:
        cashier = Cashier.query.get(cashier_id)
        if cashier:
            return cashier, 'session'
    
    return None, None


def therapist_required(f):
    """Decorator to require therapist authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        therapist, auth_method = get_current_therapist()
        if not therapist:
            return jsonify({'error': 'Authentication required'}), 401
        request.current_therapist = therapist
        request.auth_method = auth_method
        return f(*args, **kwargs)
    return decorated_function


def cashier_required(f):
    """Decorator to require cashier authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        cashier, auth_method = get_current_cashier()
        if not cashier:
            return jsonify({'error': 'Authentication required'}), 401
        request.current_cashier = cashier
        request.auth_method = auth_method
        return f(*args, **kwargs)
    return decorated_function
