import os
from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
uri = os.environ.get("DATABASE_URL")

if not uri:
    raise Exception("DATABASE_URL not set")

if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
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

        user = db.session.get(User, session['user_id'])
        if not user or not user.is_admin:
            return redirect(url_for('login'))

        return f(*args, **kwargs)
    return decorated

def get_completed():
    rows = db.session.query(Completion).filter_by(user_id=session['user_id']).all()
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
            session['is_admin'] = user.is_admin
            return redirect(url_for('home'))
        return render_template('login.html', error='Incorrect username or password.', username=username)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── Admin routes ──────────────────────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin():
    users = db.session.query(User).order_by(User.created_at.desc()).all()
    return render_template('admin.html', users=users)


@app.route('/admin/create', methods=['POST'])
@admin_required
def admin_create_user():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    is_admin = request.form.get('is_admin') == 'on'

    if not username or not password:
        flash('Username and password are required.', 'error')
        return redirect(url_for('admin'))

    existing = db.session.query(User).filter_by(username=username).first()
    if existing:
        flash(f'Username "{username}" already exists.', 'error')
        return redirect(url_for('admin'))

    user = User(username=username, is_admin=is_admin)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    flash(f'User "{username}" created successfully.', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/delete/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    if user_id == session.get('user_id'):
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin'))

    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin'))

    db.session.query(Completion).filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()

    flash(f'User "{user.username}" deleted.', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/toggle/<int:user_id>', methods=['POST'])
@admin_required
def admin_toggle_admin(user_id):
    if user_id == session.get('user_id'):
        flash('You cannot change your own admin status.', 'error')
        return redirect(url_for('admin'))

    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin'))

    user.is_admin = not user.is_admin
    db.session.commit()

    flash(f'Admin status updated for "{user.username}".', 'success')
    return redirect(url_for('admin'))

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
    already = db.session.query(Completion).filter_by(
        user_id=session['user_id'], section_name=item
    ).first()
    if not already:
        db.session.add(Completion(user_id=session['user_id'], section_name=item))
        db.session.commit()
    return redirect(request.referrer or url_for('home'))

@app.route('/undo/<item>')
@login_required
def undo(item):
    db.session.query(Completion).filter_by(
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
    # For production, use a WSGI server like Gunicorn instead of Flask's built-in server.
    app.run(host="0.0.0.0", port=5000)