from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, request, session, flash, send_file, jsonify, redirect, render_template,  url_for

from jetcheck.auth import (login_instructor, logout_instructor, required_instructor_login, required_tsession, validate_email, is_valid_password)
from jetcheck.models import FileList, Institute, Instructor, Tokens, Student, db
from jetcheck.models.turnitin import Assignment
from jetcheck.secrets import KEY
from jetcheck import app

import wtapi, jwt, os


instructor = Blueprint("instructor", __name__, url_prefix="/instructor")

@instructor.route('/profile/create/<string:token>', methods=['GET', 'POST'])
def create_profile(token):
    try:
        decoded = jwt.decode(token, KEY, algorithms=['HS256'])
        account:Instructor = Instructor.query.filter(Instructor.id == decoded['instructor_id'], Instructor.email == decoded['instructor_email']).first()

        delta = account.end_date - datetime.now().date()
        duration = timedelta(days=delta.days)
        expiration = datetime.utcnow() + duration

        token = jwt.encode({'user': f"{account.email}", "duration": f"{duration}", 'exp': expiration}, KEY)

        # print("new_token\n", token)
        if account.is_verified != 0:
            return redirect(url_for('instructor.login'))

        if request.method == "POST":
            first_name = request.form['insFirstName']
            last_name = request.form['insLastName']
            contact = request.form['insContact'] if request.form['insContact'] else None
            password = request.form['insPassword']
            institute_name = request.form['insInstituteName']

            if first_name and last_name and password:
                if len(password) < 8:
                    return render_template("instructor/create_profile.html", error="Password must be at least 8 characters and contain letters, symbols and numbers.") 
                account.is_verified = True
                account.first_name = first_name
                account.last_name = last_name
                account.contact = contact             
                account.password = generate_password_hash(password)

                t = Tokens(instructor=account, token=token)
                i = Institute(instructor=account, name=institute_name)

                db.session.add_all([account, t, i])
                db.session.commit()
                return redirect(url_for('instructor.login'))

        return render_template("instructor/create_profile.html")
    except Exception as e:
        print(e)
        return jsonify(error=1, message="Token is Invalid or Expired")
    

@instructor.route('/login/', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        data = request.get_json()
        account: Instructor = Instructor.query.filter(Instructor.email == data['email']).first()
        # print(generate_password_hash("12345678"))
        
        if account and check_password_hash(account.password, data['password']):
            if account.account_sts != 1:
                return jsonify(error="Your account is locked by Admin")
            print(datetime.date(datetime.now()))
            if account.end_date < datetime.now().date():
                return jsonify(error="Your account is expired please contact your Admin")
            # user.is_logged_in = True
            account.last_login = datetime.now()
            db.session.add(account)
            db.session.commit()
            login_instructor(account)
            
            return jsonify({"url": url_for("wtapi_login", token=session['instructor_token']) + "?next="+ url_for('instructor.index')})
        return jsonify(error="Invalid Email or Password")
            
    return render_template("login.html", title="Instructor Login")


@instructor.route('/logout/')
@required_instructor_login
def logout():
    logout_instructor()
    return redirect(url_for('instructor.login'))


@instructor.route('/')
@required_instructor_login
def index():
    try:
        now = datetime.now().date()
        ta_list = db.session.query(Student).order_by(Student.id.desc()).filter(Student.instructor_id == session['instructor_id']).limit(5).all()
        exp_list = db.session.query(Student).order_by(Student.id.desc()).filter(Student.end_date < now, Student.instructor_id == session['instructor_id']).limit(5).all()
        account:Instructor = Instructor.query.order_by(Instructor.id.desc()).filter(Instructor.id == session['instructor_id']).first()
        return render_template("instructor/index.html", title="Dashboard", account=account, ta_list=ta_list, exp_accounts=exp_list)
    except Exception as e:
        print(e)
        return redirect(url_for("instructor.login"))


@instructor.route('/create_token/<int:is_verified>/<string:email>/', methods=["GET", "POST"])
@required_instructor_login
def create_token(is_verified, email):
    token = jwt.encode({"instructor_id": session['instructor_id'], "completed_setup": is_verified, "email": email, "exp": datetime.utcnow() + timedelta(days=1)}, KEY, algorithm='HS256')
    return jsonify(token=token)


@instructor.route('/teacher_assistant/add/', methods=["GET", "POST"])
@required_instructor_login
def add_teacher_assistant():
    message = ""
    account = Instructor.query.filter(Instructor.id == session['instructor_id']).first()
    if (account.limit[0].total_limit - account.limit[0].enrolled) <= 0:
        message = "Your account limit has been reached to its limit please contact your administration."
        flash(message, "danger")
        return redirect(url_for("instructor.index"))
    if request.method == "POST":

        email = request.form['taEmail']
        start_date = request.form['taInitialDate']
        end_date = request.form['taExpireDate']
        account_sts = request.form['taAccountStatus']

        if not (email and start_date and end_date):
            message = "Please provide all the important(*) fields"
            flash(message, "danger")
            return redirect(url_for("instructor.add_teacher_assistant"))

        if start_date > end_date:
            message = "Please provide valid expiry date"
            flash(message, "danger")
            return redirect(url_for("instructor.add_teacher_assistant"))
        
        if not validate_email(email):
            message = "Please provide a valid email"
            flash(message, "danger")
            return redirect(url_for("instructor.add_teacher_assistant"))
            
        try:
            ta = Student()
            ta.email = email
            ta.start_date = start_date
            ta.end_date = end_date
            ta.account_sts = account_sts
            ta.instructor_id = account.id
            db.session.add(ta)
            db.session.commit()
            # return redirect(url_for('instructor.create_token', is_verified=ta.is_verified, email=ta.email))

            token = jwt.encode({"instructor_id": session['instructor_id'], "completed_setup": ta.is_verified, "email": ta.email, "exp": datetime.utcnow() + timedelta(days=1)}, KEY, algorithm='HS256')
            print(token)
            # sending email

            flash(f"Email has been sent to <strong>{ta.email}</strong>")  
        except Exception as e:
            flash(f"The email <strong>{ta.email}</strong> is added by someone else", "danger")
            return redirect(url_for("instructor.add_teacher_assistant"))

    return render_template("instructor/add_ta.html", title="Add Teacher Assistant", message=message)


@instructor.route('/teacher_assistant/edit/<int:id>', methods=["GET", "POST"])
@required_instructor_login
def edit_teacher_assistant(id):
    ta = Student.query.filter(Student.instructor_id == session['instructor_id'], Student.id == id).first()
    if ta == None:
        flash("No Account Found", "danger")
        return redirect(url_for("instructor.all_teacher_assistant"))
    if request.method == "POST":
        email = request.form['taEmail']
        start_date = request.form['taInitialDate']
        end_date = request.form['taExpireDate']
        account_sts = request.form['taAccountStatus']

        if not (email and start_date and end_date):
            flash("Please provide all the important(*) fields", "error")
            return redirect(url_for('instructor.edit_teacher_assistant', id=id))
        
        if not validate_email(email):
            flash("Please provide a valid email", "error")
            return redirect(url_for('instructor.edit_teacher_assistant', id=id))
            
        ta.email = email
        ta.start_date = start_date
        ta.end_date = end_date
        ta.account_sts = account_sts
        db.session.add(ta)
        try:
            db.session.commit()
            flash(f"<strong>{ta.email}</strong> updated successfully", "info")
        except Exception as e:
            flash(f"Duplicate entry for email <strong>{ta.email}</strong>", "info")
        return redirect(url_for('instructor.all_teacher_assistant'))

    return render_template("instructor/edit_ta.html", title="Edit Teacher Assistant", account=ta)


@instructor.route('/teacher_assistant/delete/<int:id>', methods=["POST"])
@required_instructor_login
def delete_teacher_assistant(id):
    account = Student.query.filter(Student.id == id, Student.instructor_id == session['instructor_id']).first()
    if account == None:
        flash("No Account Found", "danger")
        return redirect(url_for("instructor.all_teacher_assistant"))
    db.session.delete(account)
    db.session.commit()
    return redirect(url_for('instructor.all_teacher_assistant'))


@instructor.route('/teacher_assistant/all/')
@required_instructor_login
def all_teacher_assistant():
    per_page = request.form.get('per_page') 
    page = request.args.get('page', 1, type=int)
    ta_list = db.session.query(Student).order_by(Student.id.desc()).filter(Student.instructor_id == session['instructor_id']).paginate(page=page, per_page=per_page)
    # account = Instructor.query.filter(Instructor.id == session['instructor_id'])
    print(ta_list)
    return render_template("instructor/all_ta.html", title="All Enrolled Teachers Assistant", accounts=ta_list, now=datetime.now().date())


@instructor.route('/all_files')
@required_instructor_login
def all_files():
    account = Instructor.query.filter(Instructor.id == session['instructor_id']).first()
    important_files = FileList.query.filter(FileList.instructor_id == account.id, FileList.is_important == 1).order_by(FileList.id.desc()).all()
    files = FileList.query.filter(FileList.instructor_id == account.id, FileList.is_important == 0).order_by(FileList.id.desc()).all()
    return render_template("instructor/all_files.html", title="All Files", account=account, files=files, important_files=important_files)


@instructor.route("/upload_file/", methods=['GET', 'POST'])
@required_instructor_login
@required_tsession
def upload_file():
    current_account: Instructor  = Instructor.query.filter(Instructor.id == session['instructor_id']).first()
    if request.method == 'POST':
        file = request.files.get('file')
        title = request.form['fileTitle'] if request.form['fileTitle'] else None
        description = request.form['fileDescription'] if request.form['fileDescription'] else None
        aid = request.form['aid']
        
        if not file:
            return jsonify(error="Please select a file")
        if not title:
            return jsonify(error="Please enter Title")
        
        # if not file.content_type in settings.ALLOWED_CONTENT_TYPES:
        #     print(file.content_type)
        #     return jsonify(error="Invalid file formate")
        
        submit_file_info = wtapi.SubmitFileInfo(
            session_id=session['t_sid'],
            file_name=file.filename,
            file_title=title,
            assignment_id=aid,
            auther_fname=current_account.first_name,
            auther_lname=current_account.last_name
        ) 
        submit_response = wtapi.submit_file(submit_file_info.dict(), {"file": (file.filename, file.stream.read(), file.mimetype)}, token=session['instructor_token']).json()
        file_info = wtapi.DownloadFileInfo(
            session_id=submit_file_info.session_id,
            # file_title="TEST_MY_FILE - 55287331051630032023",
            file_title=submit_response['file_title'],
            assignment_id=submit_file_info.assignment_id,
        )
        s = wtapi.new_session()
        res = s.post(wtapi.API_FILE_INFO_URL, json=file_info.dict(), params={"token": session["instructor_token"]}).json()
        print(res)
        file=FileList()
        assignment = Assignment.query.filter(Assignment.aid == aid).first()
        file.instructor_id = current_account.id
        file.name = submit_response['file_name']
        file.title = submit_response['file_title']
        file.size = submit_response['file_size']
        file.path = os.path.join(app.config['UPLOAD_FOLDER'],"pdf", submit_response['file_title']+".pdf")
        file.description = description
        # file.plagiarism = res['plagiarism']
        file.upload_date = datetime.now().date()
        file.assignment_id = assignment.id
        # current_account.file_list = file
        db.session.add(file)
        db.session.commit()
        url = url_for("instructor.all_files")
        return jsonify(url=url)
        # return jsonify(url=f"/download-file/{file.assignment_id}/{file.title}/?view=true")
        # time.sleep(6)        
        # return redirect(url_for('download_file', assignment_id=file.assignment_id, file_title=file.title))
    ass = Assignment.query.filter(Assignment.t_account_id == session['t_id'])
    return render_template("upload.html", title="Upload File", context={"all_assignments":ass, "account":current_account})


@instructor.route("/download_file/<int:file_id>/", methods=["GET", "POST"])
@required_instructor_login
@required_tsession
def download_file(file_id):
    file = FileList.query.filter(FileList.id == file_id, FileList.instructor_id == session['instructor_id']).first()
    if file == None:
        flash("File not found", "danger")
        return redirect(url_for("instructor.all_files"))
    
    file_title = file.title

    pdf_uploads = app.config['UPLOAD_FOLDER'] +"pdf/"
    pdf_file_path = pdf_uploads+file_title+".pdf"
    is_view = False if request.args.get("view") else True

    print(pdf_file_path)
    
    if not os.path.exists(pdf_file_path):
        download_file_info = wtapi.DownloadFileInfo(
            session_id=session['t_sid'],
            file_title=file_title,
            assignment_id=file.assignment.aid
            # file_title="TEST_MY_FILE - 12591606071530032023",
        )
        
        try:
            wtapi.download_file(pdf_uploads + file_title+".pdf", download_file_info, session["instructor_token"])
        except Exception as e:
            print(e)
            return {"error": f"{e}"}
    # return ""
    return send_file("static/uploads/pdf/"+ file_title+".pdf", as_attachment=is_view)


@instructor.get("/delete_file/<int:id>")
@required_instructor_login
def delete_file(id):
    file = FileList.query.filter(FileList.id == id, FileList.instructor_id == session['instructor_id']).first()
    if file == None:
        flash("File not found", "danger")
        return redirect(url_for("instructor.all_files"))
    db.session.delete(file)
    db.session.commit()
    try:
        os.remove(file.path)
    except OSError as e:
        print(e)
        flash('Error while deleting a file')
    flash("File deletion success", "success")
    return redirect(url_for("instructor.all_files"))

    
@instructor.route("/file_important/<int:id>/<int:is_important>/")
@required_instructor_login
def file_important(id, is_important):
    is_important = True if is_important == 1 else False
    file = FileList.query.filter(FileList.id == id, FileList.instructor_id == session['instructor_id']).first()
    if file == None:
        flash("File not found", "danger")
        return redirect(url_for("instructor.all_files"))
    if file:
        file.is_important = is_important
        db.session.add(file)
        db.session.commit()
    return redirect(url_for('instructor.all_files'))


@instructor.route("/file/get/<int:id>", methods=['POST'])
@required_instructor_login
def file_by_id(id):
    file:FileList = FileList.query.filter(FileList.id == id, FileList.instructor_id == session['instructor_id']).first()
    # student: Student = Student.query.filter(Student.id==current_user.id).first()
    if not file:
        return jsonify(error="No File Found!")
    return jsonify({
        "id":file.id,
        "name":file.name,
        "title": file.title,
        "path": file.path,
        "is_important": file.is_important,
        "description": file.description,
        "plagiarism": file.plagiarism,
        "size": file.size,
        "upload_date": file.upload_date,
        "aid":file.assignment_id,
        "download_path": url_for("instructor.download_file", file_id=file.id)
    })


@instructor.route("/settings/", methods=["GET", "POST"])
@required_instructor_login
def settings():
    account = Instructor.query.filter(Instructor.id == session['instructor_id']).first() 
    return render_template("instructor/settings.html", title="Settings", account=account)


@instructor.route("/settings/update_account", methods=["POST"])
@required_instructor_login
def update_account():
    account: Instructor = Instructor.query.filter(Instructor.id == session['instructor_id']).first() 
    first_name   = request.form.get("insFirstName")
    last_name    = request.form.get("insLastName")
    contact      = request.form.get("insContact")
    old_password = request.form.get("insOldPassword")
    new_password = request.form.get("insNewPassword")

    if not (old_password):
        flash("Please provide old password", "danger")
        return redirect(url_for('instructor.settings'))

    if not (first_name and last_name):
        flash("Please provide all the required(*) fields", "danger")
        return redirect(url_for('instructor.settings'))
    
    if check_password_hash(account.password, old_password):
        if new_password:  
            print(new_password)  
            if not is_valid_password(new_password):
                msg="Password must be at least 8 characters and contain letters, symbols and numbers."
                flash(msg, "danger")
                return redirect(url_for('instructor.settings'))
            account.password = generate_password_hash(new_password)
        account.first_name = first_name
        account.last_name  = last_name
        account.contact    = contact
        db.session.add(account)
        db.session.commit()
    else:
        flash("Invalid Password", "danger")
        return redirect(url_for('instructor.settings'))
    
    flash("Account updated successfully", "success")
    return redirect(url_for('instructor.settings'))


@instructor.route("/settings/update_institute", methods=["POST"])
@required_instructor_login
def update_institute():
    account = Instructor.query.filter(Instructor.id == session['instructor_id']).first() 
    institute_name   = request.form.get("insInstituteName")
    password   = request.form.get("insPassword")
    if check_password_hash(account.password, password) == False:
        flash("Invalid password", "danger")
        return redirect(url_for('instructor.settings'))
    account.institute[0].name = institute_name
    db.session.add(account)
    db.session.commit()
    flash("Name of Institute updated successfully", "success")
    return redirect(url_for('instructor.settings'))


# @app.context_processor
@instructor.context_processor
def inject_request():
    return dict(request=request, is_instructor=True)