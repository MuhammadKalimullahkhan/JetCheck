import math
import os
from flask import (
    Flask,
    flash,
    redirect,
    request,
    jsonify,
    render_template,
    send_file,
    session,
    url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta

import docx
import ai_detector

from jetcheck.auth import is_valid_password, required_tsession
from jetcheck.secrets import KEY
from jetcheck import settings

path = os.path.abspath(".")
db = SQLAlchemy()

app = Flask(path, template_folder=__name__+"/public")
# FOR HOSTING
# app = Flask(__name__, template_folder="public")

app.config['admin_password'] = "!@0345Kalim"

app.config['SECRET_KEY'] = KEY
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///jetcheck.sqlite"
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=100000)
app.config['UPLOAD_FOLDER'] = settings.UPLOAD_DIR

from jetcheck.models import *
from jetcheck.routes import *
from jetcheck.mail import send_email_verification_mail, generate_verification_email_html
import wtapi


db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "/login"

app.register_blueprint(admin_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(instructor_blueprint)
app.register_blueprint(student_blueprint)


@login_manager.user_loader
def load_user(user_id):
    user = Student.query.get(user_id)
    return user


@app.route("/login/", methods=["GET", "POST"])
def login():
    logout_user()
    if request.method == "POST":
        data = request.get_json()
        user: Student = Student.query.filter(
            Student.email == data['email']).first()
        if user and user.is_verified != 1:
            return jsonify({"error": "Please verify your account"})
        if user and check_password_hash(user.password, data['password']):
            if datetime.now().date() > user.end_date:
                return jsonify({"error": "Your account is expired"})
            if user.account_sts != 1:
                return jsonify({"error": "Your account is locked by Instructor"})
            if user.instructor.account_sts != 1:
                return jsonify({"error": "Your's Instructor is locked by Jetcheck Team"})

            account_remaining_days = user.end_date - datetime.now().date()
            if account_remaining_days < timedelta(days=10):
                if account_remaining_days.days == 1:
                    flash(
                        f"Your account will expired after {account_remaining_days.days} day", "warning")
                flash(
                    f"Your account will expired after {account_remaining_days.days} days", "warning")
            # if user.is_logged_in:
            #     return jsonify({"error": "Student is already logged in"})
            user.last_login = datetime.now()
            # user.is_logged_in = True
            db.session.add(user)
            db.session.commit()
            login_user(user)
            session['user_email'] = user.email
            session['instructor_token'] = user.instructor.token[0].token
            return jsonify({"url": url_for("wtapi_login", token=session['instructor_token']) + "?next=" + url_for('index')})
        return jsonify(error="Invalid Email or Password")
    return render_template("login.html", title="Teacher Assistant Login")


@app.route("/ta/logout")
@login_required
def user_logout():
    current_user.is_logged_in = False
    db.session.add(current_user)
    db.session.commit()
    logout_user()
    # Delete all sessions
    session.pop("t_sid", None)
    return redirect(url_for('login'))


@app.route("/wtapi/login/<string:token>/")
def wtapi_login(token):
    next_page = request.args.get("next")
    account: AccountDetails = AccountDetails.query.filter(
        AccountDetails.is_selected == True).first()
    if account == None:
        flash("No Selected Account Found", "danger")
        return "<script>window.history.back()</script>"
    au = wtapi.login(
        {"email": account.email, "password": account.password, "token": token})
    session['t_sid'] = au['session-id']
    session['t_email'] = account.email
    session['t_id'] = account.id
    if next_page:
        return redirect(next_page)
    return redirect(url_for("index"))


@app.route("/")
@login_required
def home():
    if "t_sid" in session:
        return redirect(url_for("index"))
    return redirect(url_for("wtapi_login", token=current_user.instructor.token[0].token))


@app.route("/ta/")
@login_required
def index():
    return redirect(url_for("all_files"))


@app.route("/ta/files/all/")
@login_required
def all_files():
    important_files = FileList.query.filter(
        FileList.user_id == current_user.id, FileList.is_important == 1).order_by(FileList.id.desc()).all()
    files = FileList.query.filter(FileList.user_id == current_user.id,
                                  FileList.is_important == 0).order_by(FileList.id.desc()).all()
    return render_template("student/all_files.html", title="All Files", files=files, important_files=important_files)


@app.route("/ta/file/<int:id>", methods=['POST'])
@login_required
@required_tsession
def file_by_id(id):
    file: FileList = FileList.query.filter(
        FileList.id == id, FileList.user_id == current_user.id).first()
    if file.plagiarism == None:
        file_info = wtapi.DownloadFileInfo(
            session_id=session['t_sid'],
            file_title=file.title,
            assignment_id=file.assignment.aid,
        )

        s = wtapi.new_session()
        res = s.post(wtapi.API_FILE_INFO_URL, json=file_info.dict(), params={
                     "token": session['instructor_token']}).json()

        file.plagiarism = res['plagiarism'][0]
        db.session.add(file)
        db.session.commit()
    if not file:
        return jsonify(error="No File Found!")
    return jsonify({
        "id": file.id,
        "name": file.name,
        "title": file.title,
        "path": file.path,
        "is_important": file.is_important,
        "description": file.description,
        "plagiarism": file.plagiarism,
        "size": file.size,
        "upload_date": file.upload_date,
        "aid": file.assignment_id,
        "download_path": url_for("download_file", file_id=file.id),
        "ai": file.ai,
        "human": file.human_written
    })


@app.route("/ta/upload_file/", methods=['GET', 'POST'])
@login_required
@required_tsession
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        title = request.form['fileTitle'] if request.form['fileTitle'] else None
        description = request.form['fileDescription'] if request.form['fileDescription'] else None
        aid = request.form['aid']

        if not file:
            return jsonify(error="Please select a file")
        if not title:
            return jsonify(error="Please enter Title")

        submit_file_info = wtapi.SubmitFileInfo(
            session_id=session['t_sid'],
            file_name=file.filename,
            file_title=title,
            assignment_id=aid,
            auther_fname=current_user.first_name,
            auther_lname=current_user.last_name
        )
        submit_response = wtapi.submit_file(
            submit_file_info.dict(),
            {"file": (file.filename, file.stream.read(), file.mimetype)},
            token=session['instructor_token']
        ).json()

        if 'errorMessage' in submit_response:
            return jsonify(error=submit_response['errorMessage'], url=url_for('upload_file'))

        # detect ai content
        max_chars = 40000
        split_docs = split_docx_file(file, max_chars)
        html = []
        ai_percentages = []
        
        # Save each part as a separate document
        for i, doc_part in enumerate(split_docs):
            doc = doc_part
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            try:
                ai_response = ai_detector.detect(text)
                html.append(ai_detector.mark_changes(text, ai_response['data']['h']))
                ai_percentages.append(ai_response['data']['fakePercentage'])
            except Exception as e:
                print(e)
        ai_avg = sum(ai_percentages) / len(ai_percentages)

        file = FileList()
        assignment = Assignment.query.filter(
            Assignment.aid == int(aid)).first()
        file.user_id = current_user.id
        file.name = submit_response['file_name']
        file.title = submit_response['file_title']
        file.size = submit_response['file_size']
        file.path = os.path.join(
            app.config['UPLOAD_FOLDER'], "pdf", submit_response['file_title']+".pdf")
        file.description = description
        file.ai = round(ai_avg, 2)
        file.upload_date = datetime.now().date()
        file.assignment_id = assignment.id
        db.session.add(file)
        db.session.commit()
        return jsonify(url=url_for("all_files"))
    ass = Assignment.query.filter(Assignment.t_account_id == session['t_id'])
    return render_template("upload.html", title="Upload File", context={"all_assignments": ass})


@app.route("/download_file/<int:file_id>/")
@login_required
@required_tsession
def download_file(file_id):
    file: FileList = FileList.query.filter(
        FileList.id == file_id, FileList.user_id == current_user.id).first()
    if file == None:
        flash("File not found", "danger")
        return redirect(url_for("all_files"))

    file_title = file.title
    pdf_uploads = app.config['UPLOAD_FOLDER'] + "pdf/"
    pdf_file_path = pdf_uploads+file_title+".pdf"
    is_view = False if request.args.get("view") else True

    if not os.path.exists(pdf_file_path):
        download_file_info = wtapi.DownloadFileInfo(
            session_id=session['t_sid'],
            file_title=file_title,
            assignment_id=file.assignment.aid
        )

        try:
            wtapi.download_file(pdf_file_path, download_file_info,
                                token=session['instructor_token'])
        except Exception as e:
            print(e)
            flash("Failed: error occured while downloading, please try again.", "danger")
            return redirect(url_for("wtapi_login", token=current_user.instructor.token[0].token))
    return send_file(pdf_file_path, as_attachment=is_view)


@app.post("/delete_file/<int:file_id>")
@login_required
def delete_file(file_id):
    file = FileList.query.filter(
        FileList.user_id == current_user.id, FileList.id == file_id).first()
    if not file:
        flash("No file found", "danger")
        return redirect(url_for("all_files"))
    db.session.delete(file)
    db.session.commit()
    try:
        os.remove(file.path)
    except OSError as e:
        print(e)
        flash('Error while deleting a file')
    flash("File deletion success", "success")
    return redirect(url_for("all_files"))


def split_docx_file(file_path, max_chars):
    # Load the document
    doc = docx.Document(file_path)

    # Extract the text from the document
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"

    # Split the text into parts based on the character count
    num_parts = math.ceil(len(text) / max_chars)
    parts = []
    for i in range(num_parts):
        start_index = i * max_chars
        end_index = (i + 1) * max_chars
        part_text = text[start_index:end_index]
        parts.append(part_text)

    # Create separate documents for each part
    doc_parts = []
    for part_text in parts:
        part_doc = docx.Document()
        part_doc.add_paragraph(part_text)
        doc_parts.append(part_doc)

    return doc_parts


@app.route("/ai/upload", methods=["GET", "POST"])
@login_required
def ai_upload():
    if request.method == 'POST':
        file = request.files.get('file')
        if file == None:
            return jsonify(error="Please select a file")

        max_chars = 40000

        split_docs = split_docx_file(file, max_chars)

        html = []
        ai_percentages = []
        # Save each part as a separate document
        for i, doc_part in enumerate(split_docs):
            doc = doc_part
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            try:
                ai_response = ai_detector.detect(text)
                html.append(ai_detector.mark_changes(text, ai_response['data']['h']))
                ai_percentages.append(ai_response['data']['fakePercentage'])
            except Exception as e:
                print(e)


        ai_avg = sum(ai_percentages) / len(ai_percentages)

        return jsonify(
            content="".join([h for h in html]),
            user={
                "firstName":current_user.first_name,
                "lastName":current_user.last_name
                },
            ai=round(ai_avg, 2)
            )
    return render_template("ai_upload.html", title="AI")


@app.route("/file_important/<int:id>/<int:is_important>/")
@login_required
def file_important(id, is_important):
    is_important = True if is_important == 1 else False
    file = FileList.query.filter(
        FileList.id == id, FileList.user_id == current_user.id).first()
    
    if file:
        file.is_important = is_important
        db.session.add(file)
        db.session.commit()
    else:
        flash("File not found")
    return redirect(url_for('all_files'))


@app.route("/ta/profile/", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        password = request.form['taPassword']
        if check_password_hash(current_user.password, password):
            current_user.first_name = request.form['taFirstName']
            current_user.last_name = request.form['taLastName']
            db.session.add(current_user)
            db.session.commit()
            flash("Account updated", "success")
        else:
            flash("Invalid Password", "danger")
    return render_template("student/profile.html", title="Profile")


@app.post("/ta/update_password/")
@login_required
def update_password():
    password = request.form['taOldPassword']
    new_password = request.form['taNewPassword']

    if is_valid_password(new_password) == False:
        flash("Password must be at least 8 characters and contain letters, symbols and numbers.", "danger")
        return redirect(url_for("profile"))
    if check_password_hash(current_user.password, password):
        current_user.password = generate_password_hash(new_password)
        db.session.add(current_user)
        db.session.commit()
        flash("Password updated", "success")
    else:
        flash("Invalid Password", "danger")
    return redirect(url_for("profile"))


@app.context_processor
def inject_request():
    return dict(request=request)


with app.app_context():
    db.create_all()
    # admin = Admin(
    #     id=1,
    #     username="wazar",
    #     password=generate_password_hash("12345678")
    # )
    # token = jwt.encode({"admin_id": admin.id, "exp": datetime.utcnow() + timedelta(days=365*100)}, KEY, algorithm='HS256')

    # admin_token = Tokens(admin_id=admin.id, token=token)
    # db.session.add(admin_token)
    # db.session.commit()
#     # # sa = SuperAdmin.query.filter(
#     # #     SuperAdmin.id == 1
#     # # ).first()
#     ad = Instructor(
#         id=1,
#         admin_id=sa.id,
#         name="Kishwar Ali",
#         email="admin@wss.pk",
#         password="123456",
#         contact="1234567890",
#         start_date=datetime.now()
#     )
#     u1 = Student(
#         first_name="Muhammad Kalim",
#         last_name="Ullah",
#         email="user@wss.pk",
#         password="123456",
#         contact="1234567890",
#         instructor_id=ad.id,
#         account_sts=1,
#         start_date=datetime.now()
#     )
    # tad = AccountDetails(
    #     email="khankalimkalim121@gmail.com",
    #     password="!@Swatswat12",
    #     is_selected=True
    #    )
    # try:
    # db.session.add(tad)
    # db.session.add(sa)
    # db.session.add_all([ad, u1])
    # db.session.commit()
    # except Exception as e: print(e)
