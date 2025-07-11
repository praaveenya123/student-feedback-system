from app import app, db, User, bcrypt

# Ensure the script runs within the application context
with app.app_context():
    # Create the database tables if they don’t exist
    db.create_all()

    # Adding an Admin User
    admin_user = User(username="admin", password=bcrypt.generate_password_hash("admin123").decode('utf-8'), role="admin")
    student_user = User(username="student", password=bcrypt.generate_password_hash("student123").decode('utf-8'), role="student")

    # Check if users already exist before adding them  
    if not User.query.filter_by(username="admin").first():
        db.session.add(admin_user)
    
    if not User.query.filter_by(username="student").first():
        db.session.add(student_user)

    # Commit changes
    db.session.commit()

    print("Admin and Student users added successfully!")


