from flask import Flask, render_template, request, redirect, url_for, session, flash
from forms import RegistrationForm
from models import User
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from config import Config
from database import db  # Import db from database.py
from models import db,Feedback
from flask_migrate import Migrate



app = Flask(__name__)
app.config.from_object(Config)  # Load configs from config.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Or your DB URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

from models import User, Subject, FeedbackQuestion, FeedbackOption, FeedbackSubmission, FeedbackResponse
# Decorator to ensure user is logged in before accessing certain routes
def login_required(f):
    @wraps(f)  # preserves the original function name and docstring
    def wrap(*args, **kwargs):
        if 'user' not in session:
            flash("Please log in first!", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrap

@app.route('/')
def index():
    return render_template('index.html')  
    # Make sure you have an index.html in the templates folder

from forms import LoginForm

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Query the database for the user
        user = User.query.filter_by(username=username).first()

        # Check if user exists and the password matches
        if user and user.check_password(password):
            session['user'] = user.username
            session['role'] = user.role

            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash("Invalid username or password", "error")
    
    return render_template('login.html', form=form)
@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    # Only allow admin to register new users
    if session.get('role') != 'admin':
        flash("Only admin can register new users", "error")
        return redirect(url_for('login'))

    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        role = form.role.data
        # Capture the 'section' from the new dropdown in add_users.html
        section = request.form.get('section')

        # Check if the user already exists
        if User.query.filter_by(username=username).first():
            flash("User already exists", "error")
            return redirect(url_for('register'))

        # Create a new user with section included
        new_user = User(username=username, role=role, section=section)
        new_user.set_password(password)  # Hashes and stores the password
        db.session.add(new_user)
        db.session.commit()  # Updates the database

        flash("User registered successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('add_users.html', form=form)

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    # Ensure only admin can access
    if session.get('role') != 'admin':
        flash("Access denied! Please login as Admin.", "error")
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')

@app.route('/student_dashboard')
@login_required
def student_dashboard():
    # Ensure only student can access
    if session.get('role') != 'student':
        flash("Access denied! Please login as Student.", "error")
        return redirect(url_for('login'))
    return render_template('student_dashboard.html')


@app.route('/Show_subjects')
@login_required
def Show_subjects():
    subjects = Subject.query.all()
    return render_template('Show_subjects.html', subjects=subjects)

@app.route('/submit_feedback', methods=['POST'])
@login_required
def submit_feedback():
    if session.get('role') != 'student':
        flash("Only students can submit feedback", "error")
        return redirect(url_for('feedback_form'))

    questions = FeedbackQuestion.query.order_by(FeedbackQuestion.order).all()
    answers_list = []
    for question in questions:
        chosen_option_id = request.form.get(f"question_{question.id}")
        if chosen_option_id:
            chosen_option = FeedbackOption.query.get(chosen_option_id)
            if chosen_option:
                line = f"{question.question_text} => {chosen_option.option_text}"
                answers_list.append(line)

    feedback_text = "\n".join(answers_list)

    additional_feedback = request.form.get('additional_feedback')
    if additional_feedback:
        feedback_text += "\n\nAdditional Comments:\n" + additional_feedback

    subject_id = request.form.get('subject_id')
    # Instead of searching the Student table, we unify to 'User'
    student_user = User.query.filter_by(username=session['user']).first()
    if not student_user:
        flash("User not found!", "error")
        return redirect(url_for('feedback_form'))

    # We can set rating or not
    # rating = request.form.get('rating') or "Good"  # or some logic

    new_feedback = Feedback(
        feedback_text=feedback_text,
        subject_id=subject_id,
        student_id=student_user.id,
        # rating=rating
    )
    db.session.add(new_feedback)
    db.session.commit()

    flash("Feedback submitted successfully!", "success")
    subject = Subject.query.get(subject_id)
    return redirect(url_for('Show_subjects', subj_submitted=subject.name))

@app.route('/add_question', methods=['POST'])
@login_required
def add_question():
    if session.get('role') != 'admin':
        flash("Only admins can add questions", "error")
        return redirect(url_for('feedback_form'))

    question_text = request.form.get('question_text')
    option_texts = request.form.get('option_texts')

    # Create question
    question = FeedbackQuestion(question_text=question_text)
    db.session.add(question)
    db.session.commit()

    # Create options
    for opt in option_texts.split(','):
        opt = opt.strip()
        if opt:
            new_option = FeedbackOption(option_text=opt, question_id=question.id)
            db.session.add(new_option)
    db.session.commit()

    flash("New question added successfully!", "success")
    return redirect(url_for('feedback_form'))


@app.route('/contact')
@login_required
def contact():
    return render_template('contact.html')

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash("New passwords do not match!", "error")
            return redirect(url_for('change_password'))
        
        # Retrieve the current user from session
        user = User.query.filter_by(username=session['user']).first()
        if not user or not user.check_password(old_password):
            flash("Old password is incorrect!", "error")
            return redirect(url_for('change_password'))
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        
        flash("Password changed successfully! Please log in with your new password.", "success")
        # Clear session to force re-login
        session.clear()
        return redirect(url_for('login'))
        
    # For GET requests, simply render the change_password form
    return render_template('change_password.html')

@app.route('/logout')
@login_required
def logout():
    return render_template('logout.html')

@app.route('/add_subjects', methods=['GET', 'POST'])
@login_required
def add_subjects():
    # Only allow admin to add subjects
    if session.get('role') != 'admin':
        flash("Only admin can add subjects", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        subject_name = request.form['subject_name']
        # Create a new subject object
        new_subject = Subject(name=subject_name)
        db.session.add(new_subject)
        db.session.commit()
        flash("Subject added successfully!", "success")
        return redirect(url_for('Show_subjects'))
    
    return render_template('add_subjects.html')

@app.route('/delete_question/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    if session.get('role') != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('feedback_form'))

    question = FeedbackQuestion.query.get(question_id)
    
    if question:
        db.session.delete(question)
        db.session.commit()
        flash("Question deleted successfully!", "success")
    else:
        flash("Question not found!", "danger")

    return redirect(url_for('feedback_form'))


@app.route('/edit_subjects/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def edit_subjects(subject_id):
    if session.get('role') != 'admin':
        flash("Only admin can edit subjects", "error")
        return redirect(url_for('login'))

    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST':
        subject.name = request.form['subject_name']
        db.session.commit()
        flash("Subject updated successfully!", "success")
        return redirect(url_for('Show_subjects'))

    return render_template('edit_subjects.html', subject=subject)

@app.route('/edit_subjects', methods=['GET'])
@login_required
def list_subjects_for_edit():
    if session.get('role') != 'admin':
        flash("Only admin can edit subjects", "error")
        return redirect(url_for('login'))

    subjects = Subject.query.all()
    return render_template('edit_subjects.html', subjects=subjects)

@app.route('/feedback', methods=['GET'])
@login_required
def feedback_form():
    # If you only want students to fill out the form, handle that in the template or here.
    
    # Grab subject_id from the query string: /feedback?subject_id=2
    selected_subject_id = request.args.get('subject_id', type=int)

    questions = FeedbackQuestion.query.order_by(FeedbackQuestion.order).all()
    subjects = Subject.query.all()

    return render_template(
        'feedback.html',
        questions=questions,
        subjects=subjects,
        selected_subject_id=selected_subject_id
    )
@app.route('/view_feedback')
@login_required
def view_feedback():
    if session.get('role') != 'admin':
        flash("Only admin can view feedback", "error")
        return redirect(url_for('login'))

    # 1. If no 'section' param is provided, just show the "cards" screen (IT-A, IT-B, All).
    section = request.args.get('section')
    if not section:
        return render_template('view_feedback.html', section=None)

    # 2. If section is provided, filter feedback and build aggregator.
    if section == 'All':
        feedbacks = Feedback.query.all()
    else:
        # Filter by user.section
        feedbacks = (Feedback.query
                     .join(User, Feedback.student_id == User.id)
                     .filter(User.section == section)
                     .all())
    
    # Build aggregator: subject -> { total, Good, Very Good,Poor, Outstanding }
    from collections import defaultdict
    subject_stats = defaultdict(lambda: {'total': 0, 'Good': 0, 'Very Good': 0, 'Poor': 0, 'Outstanding': 0})
    # Also group feedback by subject for listing comments
    grouped_feedback = defaultdict(list)

    for fb in feedbacks:
        subj_name = fb.subject_id  # or if you store subject as string, use fb.subject
        # If you are storing subject as an integer ID, retrieve it:
        subj = Subject.query.get(fb.subject_id)
        subject_name = subj.name if subj else "Unknown"

        subject_stats[subject_name]['total'] += 1
        # If you are storing rating in fb.rating, increment the aggregator
        if fb.rating in subject_stats[subject_name]:
            subject_stats[subject_name][fb.rating] += 1

        # Group feedback text so we can display them per subject
        grouped_feedback[subject_name].append(fb.feedback_text)

    # Convert aggregator counts to percentages
    subject_percentages = {}
    for subj_name, stats in subject_stats.items():
        total = stats['total']
        subject_percentages[subj_name] = {
            'total': total,
            'Good': round((stats['Good'] / total * 100), 2) if total else 0,
            'Very Good': round((stats['Very Good'] / total * 100), 2) if total else 0,
            'Outstanding': round((stats['Outstanding'] / total * 100), 2) if total else 0,
            'Poor': round((stats['Poor'] / total * 100), 2) if total else 0,
        }

    return render_template(
        'view_feedback.html',
        section=section,
        subject_percentages=subject_percentages,
        grouped_feedback=grouped_feedback
    )


@app.route('/delete_feedback/<int:feedback_id>', methods=['POST'])
@login_required
def delete_feedback(feedback_id):
    if session.get('role') != 'admin':
        flash("Only admin can delete feedback", "error")
        return redirect(url_for('view_feedback'))
    
    feedback_record = Feedback.query.get_or_404(feedback_id)
    db.session.delete(feedback_record)
    db.session.commit()
    flash("Feedback deleted successfully!", "success")
    return redirect(url_for('view_feedback'))

if __name__ == '__main__':
     with app.app_context():
        db.create_all()
     app.run(debug=True)
