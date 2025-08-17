from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model
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

# Home page - list tasks
@app.route('/')
def index():
    tasks = Task.query.order_by(Task.due_date).all()
    return render_template('index.html', tasks=tasks)

# Add task
@app.route('/add', methods=['POST'])
def add():
    new_task = Task(
        item=request.form['item'],
        class_org=request.form['class_org'],
        due_date=request.form['due_date'],
        do_date=request.form['do_date'],
        difficulty=request.form['difficulty'],
        length=request.form['length'],
        comments=request.form['comments']
    )
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))

# Delete task
@app.route('/delete/<int:id>')
def delete(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

# Edit task
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        task.item = request.form['item']
        task.class_org = request.form['class_org']
        task.due_date = request.form['due_date']
        task.do_date = request.form['do_date']
        task.difficulty = request.form['difficulty']
        task.length = request.form['length']
        task.comments = request.form['comments']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', task=task)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
