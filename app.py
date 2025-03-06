from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask App
app = Flask(__name__)
app.secret_key = "secret_key"  # Used for session management

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db = SQLAlchemy(app)

# Define Task Model (Table)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID
    title = db.Column(db.String(200), nullable=False)  # Task title
    completed = db.Column(db.Boolean, default=False)  # Task status

# Define User Model (Table for authentication)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID
    username = db.Column(db.String(80), unique=True, nullable=False)  # Username
    password = db.Column(db.String(80), nullable=False)  # Password (hashed)

# Home Page - Display Tasks
@app.route('/')
def index():
    if 'user' in session:  # Check if user is logged in
        tasks = Task.query.all()  # Fetch all tasks from database
        return render_template('index.html', tasks=tasks)
    return redirect(url_for('login'))  # Redirect to login page if not logged in

# Add a New Task
@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title')  # Get task title from form
    if title:
        new_task = Task(title=title)
        db.session.add(new_task)  # Add task to database
        db.session.commit()  # Save changes
    return redirect(url_for('index'))

# Mark Task as Complete
@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    task = Task.query.get(task_id)  # Fetch task by ID
    if task:
        task.completed = True
        db.session.commit()  # Save changes
    return redirect(url_for('index'))

# Delete a Task
@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get(task_id)  # Fetch task by ID
    if task:
        db.session.delete(task)  # Delete task
        db.session.commit()  # Save changes
    return redirect(url_for('index'))

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user'] = user.username
            return redirect(url_for('index'))
    return render_template('login.html')

# User Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Run App
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
