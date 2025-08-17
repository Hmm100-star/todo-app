import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

# Use DATABASE_URL from Render environment, fallback to local SQLite
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///tasks.db"  # fallback for local testing
)

# Render free-tier PostgreSQL uses "postgres://" but SQLAlchemy requires "postgresql+psycopg://"
if DATABASE_URL.startswith("postgres://"):
    # Convert to format compatible with SQLAlchemy and psycopg[binary]
    # psycopg[binary] supports "postgresql+psycopg://"
    DATABASE_URL = re.sub(r'^postgres://', 'postgresql+psycopg://', DATABASE_URL)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database model ---
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(200), nullable=False)
    class_org = db.Column(db.String(200))
    due_date = db.Column(db.String(50))
    do_date = db.Column(db.String(50))
    difficulty = db.Column(db.String(50))
    length = db.Column(db.String(50))
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- Routes ---
@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'due_date')  # default sort
    if sort_by == 'do_date':
        tasks = Task.query.order_by(Task.do_date).all()
    else:
        tasks = Task.query.order_by(Task.due_date).all()
    return render_template('index.html', tasks=tasks, sort_by=sort_by)

@app.route('/add', methods=['POST'])
def add():
    new_task = Task(
        item=request.form['item'],
        class_org=request.form.get('class_org'),
        due_date=request.form.get('due_date'),
        do_date=request.form.get('do_date'),
        difficulty=request.form.get('difficulty'),
        length=request.form.get('length'),
        comments=request.form.get('comments')
    )
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        task.item = request.form['item']
        task.class_org = request.form.get('class_org')
        task.due_date = request.form.get('due_date')
        task.do_date = request.form.get('do_date')
        task.difficulty = request.form.get('difficulty')
        task.length = request.form.get('length')
        task.comments = request.form.get('comments')
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', task=task)

# --- Template filter to format dates ---
@app.template_filter('short_date')
def short_date(date_str):
    """Format YYYY-MM-DD to 'Aug 12' style without year."""
    if not date_str:
        return ""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%b %d")
    except ValueError:
        return date_str

# --- Run ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # create tables automatically
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))