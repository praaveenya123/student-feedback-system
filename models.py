from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    section = db.Column(db.String(10))  # e.g., "IT-A" or "IT-B"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

# If you still want dynamic questions, keep these:
class FeedbackQuestion(db.Model):
    __tablename__ = 'feedback_question'
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, default=0)
    options = db.relationship('FeedbackOption', backref='question', lazy=True)

class FeedbackOption(db.Model):
    __tablename__ = 'feedback_option'
    id = db.Column(db.Integer, primary_key=True)
    option_text = db.Column(db.String(50), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('feedback_question.id'), nullable=False)

class FeedbackSubmission(db.Model):
    __tablename__ = 'feedback_submission'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    responses = db.relationship('FeedbackResponse', backref='submission', lazy=True)

class FeedbackResponse(db.Model):
    __tablename__ = 'feedback_response'
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('feedback_submission.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('feedback_question.id'), nullable=False)
    selected_option_id = db.Column(db.Integer, db.ForeignKey('feedback_option.id'), nullable=False)
    
    question = db.relationship('FeedbackQuestion', lazy=True)
    option = db.relationship('FeedbackOption', lazy=True)

# Comment out or remove Student model:
# class Student(db.Model):
#     ...

# Final unified Feedback model referencing user and subject
class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    feedback_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.String(20), nullable=True)  # e.g., "Good", "Excellent", or "Outstanding"
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # relationships
    subject = db.relationship('Subject', backref='feedbacks', lazy=True)
    student = db.relationship('User', backref='feedbacks', lazy=True)
