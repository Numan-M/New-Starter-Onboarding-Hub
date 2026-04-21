import os
from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ── Models ────────────────────────────────────────────────────────────────────
class User(db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin      = db.Column(db.Boolean, default=False, nullable=False)
    created_at    = db.Column(db.DateTime, server_default=db.func.now())
    completions   = db.relationship('Completion', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Completion(db.Model):
    __tablename__ = 'completions'
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    section_name = db.Column(db.String(120), nullable=False)
    completed_at = db.Column(db.DateTime, server_default=db.func.now())

# ── Sections ──────────────────────────────────────────────────────────────────
SECTIONS = [
    "Welcome", "Training", "Authentication", "Equipment",
    "Information sources", "Organisation structure", "myHR", "Employee benefits"
]
ACCESS_SECTIONS = [
    "Jira", "Confluence", "Figma", "ServiceNow",
    "Service accounts", "Developer folders", "Developer tools"
]

# ── Auth helpers ──────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated

def get_completed():
    rows = Completion.query.filter_by(user_id=session['user_id']).all()
    return [r.section_name for r in rows]

# ── Auth routes ───────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            return redirect(url_for('home'))
        return render_template('login.html', error='Incorrect username or password.', username=username)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── App routes ────────────────────────────────────────────────────────────────
@app.route('/')
@login_required
def home():
    return redirect(url_for('general', section_name=SECTIONS[0]))

@app.route('/general/<section_name>')
@login_required
def general(section_name):
    return render_page(current_item=section_name)

@app.route('/access/<tool>')
@login_required
def access(tool):
    return render_page(current_item=tool)

@app.route('/complete/<item>')
@login_required
def complete(item):
    already = Completion.query.filter_by(
        user_id=session['user_id'], section_name=item
    ).first()
    if not already:
        db.session.add(Completion(user_id=session['user_id'], section_name=item))
        db.session.commit()
    return redirect(request.referrer or url_for('home'))

@app.route('/undo/<item>')
@login_required
def undo(item):
    Completion.query.filter_by(
        user_id=session['user_id'], section_name=item
    ).delete()
    db.session.commit()
    return redirect(request.referrer or url_for('home'))

def render_page(current_item=None):
    return render_template(
        'index.html',
        sections=SECTIONS,
        access_sections=ACCESS_SECTIONS,
        current_item=current_item,
        completed=get_completed(),
        content="Placeholder"
    )
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)