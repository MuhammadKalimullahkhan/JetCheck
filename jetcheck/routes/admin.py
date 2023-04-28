from werkzeug.security import check_password_hash, generate_password_hash
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from jetcheck.models import *
from jetcheck.secrets import KEY
from jetcheck.auth import required_admin_login, logout_admin, login_admin, required_tsession

import wtapi
import jwt
import datetime


admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route('/login/', methods=['POST', 'GET'])
def login():
    logout_admin()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        spa = Admin.query.filter(Admin.username == username).first()
        if spa and check_password_hash(spa.password, password):
            login_admin(spa)
            flash("Login successfully", "success")
            spa.last_login = datetime.datetime.now().date()
            db.session.add(spa)
            db.session.commit()
            return redirect(url_for('admin.index'))
        else:
            flash("invalid username or password", "danger")
            return redirect(url_for("admin.login"))

        # if not spa:
    return render_template('admin/login.html', title="Admin Login")


@admin.route('/logout/')
@required_admin_login
def logout():
    logout_admin()
    flash("Logged Out", "info")
    return redirect(url_for('admin.login'))


@admin.route('/')
@required_admin_login
def index():
    return render_template("admin/index.html", title="Dashboard")


# ######################( INSTRUCTOR )######################
@admin.route('/accounts/instructor/')
@required_admin_login
def all_instructors():
    instructors = db.session.query(Instructor, Admin).join(Admin).order_by(Instructor.id.desc()).all()
    return render_template("admin/instructor/all_instructor.html", title="All Instructors", data={"accounts":instructors})


@admin.route('/accounts/instructor/add', methods=['GET', 'POST'])
@required_admin_login
def add_instructors():
    if request.method == "POST":
        instructor = Instructor(
            admin_id=request.form['insAdmin'],
            email=request.form['insEmail'],
            start_date=request.form['insInitialDate'],
            end_date=request.form['insExpireDate'],
            account_sts=request.form['insAccountStatus']
        )
        limit = InstructorLimit(
            instructor=instructor,
            enrolled=request.form['insEnrolled'],
            total_limit=request.form['insTotalLimit'],
        )
        
        db.session.add_all([instructor, limit])
        db.session.commit()

        # TODO Send this token to the user on email.
        token = jwt.encode({"instructor_id": instructor.id, "instructor_status":instructor.account_sts, "instructor_email": instructor.email, "admin_id":instructor.admin_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)}, KEY, algorithm='HS256')
        flash("Instructor added successfully","success")
        return redirect(url_for("auth.verify_token", token=token))
        # send_email(token)

    admins = Admin.query.all()
    return render_template("admin/instructor/add_instructor.html", title="Add Instructors", data={"admins":admins})


@admin.route('/accounts/instructor/edit/<int:id>', methods=['GET', 'POST'])
@required_admin_login
def edit_instructors(id):
    account = Instructor.query.filter(Instructor.id == id).first()
    admins = Admin.query.all()
    if request.method == "POST":
        account.email = request.form['insEmail']
        account.start_date = request.form['insInitialDate']
        account.end_date = request.form['insExpireDate']
        account.account_sts = request.form['insAccountStatus']
        account.admin_id = request.form['insAdmin']
        db.session.add(account)
        db.session.commit()
        return redirect(url_for("admin.all_instructors"))
    return render_template("admin/instructor/edit_instructor.html", title="Edit Instructor", account=account, admins=admins)


@admin.route('/accounts/instructor/delete/<int:id>', methods=['POST'])
@required_admin_login
def delete_instructors(id):
    account = db.session.query(Instructor).filter(Instructor.id == id).first()
    if account:
        db.session.delete(account)
        db.session.commit()
        flash("Instructor deleted successfully","success")
    return redirect(url_for('admin.all_instructors'))


@admin.route('/accounts/instructor/refresh_token/<int:id>', methods=['POST'])
@required_admin_login
def refresh_token_for_instructor(id):
    instructor = Instructor.query.filter(Instructor.id == id).first()
    if instructor:
        token = jwt.encode({"instructor_id": instructor.id, "instructor_status":instructor.account_sts, "instructor_email": instructor.email, "admin_id":instructor.admin_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)}, KEY, algorithm='HS256')
        print(token)
        # TODO: send token to instructor on email
        flash("Verification email has been send to the Instructor's email","success")

    return redirect(url_for('admin.all_instructors'))

# ######################( END INSTRUCTOR )######################


# ######################( TA )######################
@admin.route('/accounts/teacher_assistant/')
@required_admin_login
def all_students():
    accounts = db.session.query(Student, Instructor).join(Instructor).order_by(Student.id.desc()).all()
    return render_template("admin/all_students.html", title="All Teacher Assistants", data={"accounts":accounts})


@admin.route('/accounts/teacher_assistant/add/', methods=['GET', 'POST'])
@required_admin_login
def add_students():
    if request.method == "POST":
        student = Student()
        instructor_id = request.form['stdInstructor']
        instructor = Instructor.query.filter(Instructor.id == int(instructor_id)).first()
        
        student.email = request.form['stdEmail']
        student.start_date = request.form['stdInitialDate']
        student.end_date = request.form['stdExpireDate']
        student.account_sts = request.form['stdAccountStatus']
        # student.instructor_id = instructor_id
        student.instructor = instructor

        db.session.add(student)
        db.session.commit()
        
        flash("Email has been sent to the TA's email", "success")
        return redirect(url_for("admin.all_students"))

    instructors = Instructor.query.all()
    return render_template("admin/add_students.html", title="Add Teacher Assistant", instructors=instructors)


@admin.route('/accounts/teacher_assistant/edit/<int:id>', methods=["GET", "POST"])
@required_admin_login
def edit_students(id):
    student: Student = db.session.query(Student).filter(Student.id == id).first()
    if request.method == "POST":
        student.first_name = request.form['stdFirstName']
        student.last_name = request.form['stdLastName']
        student.email = request.form['stdEmail']
        student.contact = request.form['stdContact']
        student.start_date = request.form['stdInitialDate']
        student.end_date = request.form['stdExpireDate']
        student.account_sts = request.form['stdAccountStatus']
        student.std_instructor.id = request.form['stdInstructor']

        db.session.add(student)
        db.session.commit()
        
    return render_template("admin/edit_students.html", title="Edit Teacher Assistant", student=student)


@admin.route('/accounts/teacher_assistant/delete/<int:id>', methods=["POST"])
@required_admin_login
def delete_students(id):
    student: Student = Student.query.filter(Student.id == id).first()
    db.session.delete(student)
    db.session.commit()
    flash("TA deleted successfully","success")
    return redirect(url_for('admin.all_students'))

# ######################( END TA )######################


@admin.route('/settings/')
@required_admin_login
def settings():
    current_admin = Admin.query.filter(Admin.id == session['admin_session_id']).first()
    turnitin_accounts = AccountDetails.query.all()
    return render_template("admin/settings.html", title="Settings",  data = {
        'current_admin':current_admin,
        't_accounts':turnitin_accounts,
    })

@admin.post("/update/")
@required_admin_login
def update_account():
    username = request.form.get("username")
    password = request.form.get("oldPassword")
    new_password = request.form.get("newPassword")

    account = Admin.query.filter(Admin.id == session['admin_session_id']).first()
    if check_password_hash(account.password, password):
        if new_password:
            account.password = generate_password_hash(new_password)
        account.username = username
        db.session.add(account)
        db.session.commit()
        flash("Account updated successfully", "success")
    else:
        flash("Invalid username or password", "danger")
    return redirect(url_for("admin.settings"))


# ######################( TURNITIN SETTINGS )######################
@admin.route("/set_assignments/")
@required_admin_login
@required_tsession
def set_assignments():
    account:AccountDetails = AccountDetails.query.filter(
        AccountDetails.is_selected == True).first()
    ass = Assignment.query.filter(Assignment.t_account_id == account.id).all()
    for a in ass:
        db.session.delete(a)
    db.session.commit()
    # sid = wtapi.fresh_login({"email":account.email, "password":account.password})['session-id']
    # dt = datetime.strptime(date_string, '%m/%d/%Y %H:%M:%S')
    # formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
    t_assignments:dict = wtapi.getAssignments(session['t_sid'], 0)
    assignments = []
    for assignment in t_assignments:
        new_assignment = Assignment()
        new_assignment.t_account_id = account.id
        new_assignment.aid = assignment['aid']
        new_assignment.title = assignment['title']
        new_assignment.submissions = assignment['info']
        new_assignment.url = assignment['submission']
        new_assignment.start_date = datetime.datetime.strptime(assignment['dates']['start'], '%m/%d/%Y %H:%M:%S')
        new_assignment.post_date = datetime.datetime.strptime(assignment['dates']['post'], '%m/%d/%Y %H:%M:%S')
        new_assignment.due_date = datetime.datetime.strptime(assignment['dates']['due'], '%m/%d/%Y %H:%M:%S')
        assignments.append(new_assignment)
    db.session.add_all(assignments)
    db.session.commit()
    flash("Assignments set successfully","success")
    return redirect(url_for('admin.settings') + "#assignments")


@admin.post("/add_turnitin_account/")
@required_admin_login
def add_turnitin_account():
    email = request.form.get('tEmail')
    password = request.form.get('tPassword')

    if email and password:
        account = AccountDetails(email=email, password=password)
        db.session.add(account)
        db.session.commit()
        flash("New turnitin account is affiliated","success")
    else:
        flash("Email and Password both are required","danger")
    return redirect(url_for("admin.settings")+ "#turnitin")


@admin.post("/turnitin_account/delete/<int:id>")
@required_admin_login
def delete_turnitin_account(id):
    account = AccountDetails.query.filter(AccountDetails.id == id).first()
    db.session.delete(account)
    db.session.commit()
    flash("Turnitin account removed","info")
    return redirect(url_for("admin.settings"))


@admin.route('set_turnitin_account/', methods=['POST'])
@required_admin_login
@required_tsession
def set_turnitin_account():
    account_id = request.form.get('account_id')
    selected_accounts = AccountDetails.query.filter(AccountDetails.is_selected == True).all()
    not_selected_account = AccountDetails.query.filter(AccountDetails.id == int(account_id)).first()

    not_selected_account.is_selected = True
    for selected_account in selected_accounts:
        selected_account.is_selected = False
        db.session.add(selected_account)

    db.session.add(not_selected_account)
    db.session.commit()
    wtapi.logout(session['t_sid'])
    flash("Turnitin account has been changed","success")
    return redirect(url_for('wtapi_login', token=session['admin_token']))


@admin.route('allow_assignments/', methods=['POST'])
@required_admin_login
def allow_assignments():
    assignment_id = request.form.get('account_id')
    not_selected_assignments:Assignment = Assignment.query.filter(Assignment.id == int(assignment_id)).first()
    not_selected_assignments.is_allowed = not not_selected_assignments.is_allowed

    db.session.add(not_selected_assignments)
    db.session.commit()
    flash("Assignment restriction/unrestriction success","success")
    return redirect(url_for('admin.settings'))


# TODO Assignment restriction
# ######################( END TURNITIN SETTINGS )######################


@admin.context_processor
def inject_request():
    return dict(request=request)
