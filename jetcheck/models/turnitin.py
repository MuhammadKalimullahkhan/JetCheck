from jetcheck import db


class AccountDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    is_selected = db.Column(db.Boolean, default=False)
    
    assignments = db.relationship('Assignment', backref='account_details', lazy=True)


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aid = db.Column(db.Integer, nullable=False, unique=True)
    t_account_id = db.Column(db.Integer, db.ForeignKey('account_details.id'))
    title = db.Column(db.String(120), nullable=False)
    submissions = db.Column(db.String(10), nullable=False)
    url = db.Column(db.String(120), nullable=False)
    start_date = db.Column(db.DateTime)
    post_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    is_allowed = db.Column(db.Boolean, default=True)

    files = db.relationship('FileList', backref='assignment', lazy=True)