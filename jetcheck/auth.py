from flask import session, redirect, url_for
from functools import wraps
import re

def validate_email(email):
    # Define a regular expression pattern for email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    # Use re.match() to check if the email matches the pattern
    match = re.match(pattern, email)
    # If the match is not None, the email is valid
    if match and len(email) > 3:
        return True
    else:
        return False

def is_valid_password(password):
    """Returns True if password is valid, False otherwise"""
    # Password must be at least 8 characters long
    if len(password) < 8:
        return False

    # Password must contain at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False

    # Password must contain at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False

    # Password must contain at least one digit
    if not re.search(r'\d', password):
        return False

    # Password must contain at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False

    # Password is valid
    return True

def required_admin_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not ("admin_session_id" in session):
            return redirect(url_for('admin.login'))
        return func(*args, **kwargs)
    return wrapper


def required_instructor_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not ("instructor_id" in session):
            return redirect(url_for('instructor.login'))
        return func(*args, **kwargs)
    return wrapper


def login_admin(admin):
    session['admin_session_id'] = admin.id
    session['admin_token'] = admin.token[0].token


def login_instructor(account):
    session['instructor_email'] = account.email
    session['instructor_id'] = account.id
    session['instructor_token'] = account.token[0].token


def logout_admin():
    session.pop("admin_session_id", None)


def logout_instructor():
    session.pop("instructor_email", None)
    session.pop("instructor_id", None)


def required_tsession(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not ("t_sid" in session):
            if "ta_token" in session:
                return redirect(url_for('wtapi_login', token=session['ta_token']))
            elif "instructor_token" in session:
                return redirect(url_for('wtapi_login', token=session['instructor_token']))
            else:
                return redirect(url_for('wtapi_login', token=session['admin_token']))
        return func(*args, **kwargs)
    return wrapper
