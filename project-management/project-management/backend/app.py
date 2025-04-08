from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Configure PostgreSQL database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/database_name'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask-SQLAlchemy
db = SQLAlchemy(app)

# Company Table
class Company(db.Model):
    __tablename__ = "company"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    subscription_plan = db.Column(db.String, nullable=False)

    # Relationships
    teams = db.relationship("Team", back_populates="company")
    users = db.relationship("User", back_populates="company")

    def __repr__(self):
        return f'<Company {self.name}>'

# Team Table
class Team(db.Model):
    __tablename__ = "team"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)

    # Relationships
    company = db.relationship("Company", back_populates="teams")
    userteams = db.relationship("UserTeam", back_populates="team")
    tasks = db.relationship("Task", back_populates="team")

    def __repr__(self):
        return f'<Team {self.name}>'

# User Table
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    role = db.Column(db.String, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)

    # Relationships
    company = db.relationship("Company", back_populates="users")
    userteams = db.relationship("UserTeam", back_populates="user")
    comments = db.relationship("Comment", back_populates="user")

    def __repr__(self):
        return f'<User {self.name}>'

# UserTeam Table (Junction Table for Many-to-Many between User and Team)
class UserTeam(db.Model):
    __tablename__ = "userteam"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=False)
    is_active = db.Column(db.SmallInteger, nullable=False, default=1)

    # Relationships
    user = db.relationship("User", back_populates="userteams")
    team = db.relationship("Team", back_populates="userteams")

    def __repr__(self):
        return f'<UserTeam user_id={self.user_id}, team_id={self.team_id}>'

# Task Table
class Task(db.Model):
    __tablename__ = "task"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=False)
    status = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team = db.relationship("Team", back_populates="tasks")
    comments = db.relationship("Comment", back_populates="task")

    def __repr__(self):
        return f'<Task {self.name}>'

# Comment Table
class Comment(db.Model):
    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    task = db.relationship("Task", back_populates="comments")
    user = db.relationship("User", back_populates="comments")

    def __repr__(self):
        return f'<Comment id={self.id}>'

# Create the database tables within the Flask application context
with app.app_context():
    db.create_all()
    print("Tables created successfully!")

# CRUD Routes for Company

# READ: List all companies
@app.route('/')
def index():
    companies = Company.query.all()
    return render_template('index.html', companies=companies)

# CREATE: Add a new company
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form['name']
        subscription_plan = request.form['subscription_plan']
        new_company = Company(name=name, subscription_plan=subscription_plan)
        db.session.add(new_company)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create.html')

# UPDATE: Edit a company
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    company = Company.query.get_or_404(id)
    if request.method == 'POST':
        company.name = request.form['name']
        company.subscription_plan = request.form['subscription_plan']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update.html', company=company)

# DELETE: Remove a company
@app.route('/delete/<int:id>')
def delete(id):
    company = Company.query.get_or_404(id)
    db.session.delete(company)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)