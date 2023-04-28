from datetime import datetime
from flask_login import UserMixin
from jetcheck import db

from jetcheck.models.turnitin import *


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(512), nullable=False)
    last_login = db.Column(db.Date)
    account_sts = db.Column(db.Integer, default=1)

    instructors = db.relationship('Instructor', backref='admin', lazy=True, cascade="all, delete")
    token = db.relationship('Tokens', backref='admin', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"SuperAmdin<id: {self.id}, name: {self.username}, lastLogin: {self.last_login}>"


class Instructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

    first_name = db.Column(db.String(50), default=None)
    last_name = db.Column(db.String(50), default=None)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(512), default=None)
    contact = db.Column(db.String(20), default=None)
    account_sts = db.Column(db.Integer, default=2)
    start_date = db.Column(db.Date, default=datetime.now())
    end_date = db.Column(db.Date)
    last_login = db.Column(db.Date)

    students = db.relationship('Student', backref='instructor', lazy=True, cascade="all, delete")
    files = db.relationship('FileList', backref='instructor', lazy=True, cascade="all, delete")
    institute = db.relationship('Institute', backref='instructor', lazy=True, cascade="all, delete")
    token = db.relationship('Tokens', backref='instructor', lazy=True, cascade="all, delete")
    limit = db.relationship('InstructorLimit', backref='instructor', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"Instructor(id={self.id}, super_admin_id={self.admin_id}, name='{self.first_name}', email='{self.email}', password='{self.password}', contact='{self.contact}', account_sts='{self.account_sts}', start_date='{self.start_date}', end_date='{self.end_date}', last_login='{self.last_login}')"


class Student(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'))
    first_name = db.Column(db.String(50), default=None)
    last_name = db.Column(db.String(50), default=None)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(512), default=None)
    contact = db.Column(db.String(20))
    account_sts = db.Column(db.Integer, default=2)
    is_verified = db.Column(db.Boolean, default=False)
    start_date = db.Column(db.Date, default=datetime.now())
    end_date = db.Column(db.Date)
    last_login = db.Column(db.Date)

    files = db.relationship('FileList', backref='student', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"Student<id:{self.id}, name: {self.first_name}, instructor_id: {self.instructor_id}, lastLogin:{self.last_login}>"
    

class Institute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey("instructor.id"))
    name = db.Column(db.String(120), default="Jet check default institute")


class Tokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey("instructor.id"), unique=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"), unique=True)
    token = db.Column(db.String(1024))


class InstructorLimit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey("instructor.id"))
    enrolled = db.Column(db.Integer, default=0)
    total_limit = db.Column(db.Integer)


# class FilesUploadPath(db.Model):
#     id = db.Column(db.Integer, primary_key=True, )
#     category = db.Column(db.String(30), nullable=False)
#     path = db.Column(db.String(512), default="/static/uploads/")

class FileList(db.Model):
    id = db.Column(db.Integer, primary_key=True, )
    user_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'))
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))
    
    name = db.Column(db.String(50))
    title = db.Column(db.String(120))
    path = db.Column(db.String(512))
    is_important = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(1024), default="No Description")
    plagiarism = db.Column(db.Integer)
    size = db.Column(db.String(10))
    upload_date = db.Column(db.Date, default=datetime.now())

    def __repr__(self) -> str:
        return f"FileList<Name:{self.name}, Plagiarism: {self.plagiarism}, Size: {self.size}>"
