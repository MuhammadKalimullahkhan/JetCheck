from werkzeug.security import generate_password_hash
from flask import Blueprint, render_template, request, session, flash, jsonify, redirect,  url_for

from jetcheck.auth import is_valid_password
from jetcheck.models import Student, db
from jetcheck.secrets import KEY

import jwt


student = Blueprint("ta", __name__, url_prefix="/ta")

@student.route('/profile/create/<string:token>', methods=['GET', 'POST'])
def create_profile(token):
    try:
        decoded = jwt.decode(token, KEY, algorithms=['HS256'])
        account:Student = Student.query.filter(Student.email == decoded['email'], Student.instructor_id == session['instructor_id']).first()

        if account.is_verified != 0:
            flash("Your account has already been verified", "success")
            return redirect(url_for('login'))

        if request.method == "POST":
            first_name = request.form['taFirstName']
            last_name = request.form['taLastName']
            contact = request.form['taContact'] if request.form['taContact'] else None
            password = request.form['taPassword']

            if first_name and last_name and password:
                if not is_valid_password(password):
                    flash("Password must be 8 characters and must contain symbols, letters and numbers ")
                
                account.is_verified = 1
                account.first_name = first_name
                account.last_name = last_name
                account.contact = contact             
                account.password = generate_password_hash(password)
                db.session.add(account)
                db.session.commit()
                flash("Your account has been verified successfully", "success")
                return redirect(url_for('login'))
        return render_template("student/create_profile.html")
    except Exception as e:
        print(e)
        return jsonify(error=1, message="Token is Invalid or Expired")