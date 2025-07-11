
# Student Feedback System

A web-based Student Feedback System built with **Python Flask** to allow students to provide feedback on various subjects and allow admins to manage users, questions, and feedback insights.

---

## 🚀 Features

- 🔐 Admin and Student login with role-based access
- 🧾 Admin dashboard to:
  - Register new users (admin/students)
  - Add/edit/delete subjects
  - Add/delete feedback questions
  - View feedback by section with stats and comments
- 🧑‍🎓 Student dashboard to:
  - View subjects
  - Submit feedback (with multiple questions/options)
  - Change password
- 📊 Feedback results shown as percentage stats
- 🗃️ SQLite-based backend with SQLAlchemy ORM
- 🔄 Database migrations with Flask-Migrate

---

## 🛠️ Technology Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, Bootstrap (in templates)
- **Database:** SQLite with SQLAlchemy ORM
- **Authentication:** Flask sessions and password hashing (bcrypt)
- **Forms & Validation:** Flask-WTF
- **Migrations:** Flask-Migrate, Alembic

---

## 🗂️ Folder Structure

```
student_feedback_system/
├── app.py                  # Main Flask app
├── add_users.py            # Script to create initial admin/student
├── config.py               # Configurations like secret key, DB path
├── database.py             # SQLAlchemy db instance
├── models.py               # User, Feedback, Question, etc. models
├── forms.py                # Flask-WTF forms
├── templates/              # HTML pages (login, dashboard, feedback)
├── static/                 # JS/CSS files
├── migrations/             # Alembic-generated DB migration files
├── instance/               # Flask instance folder for SQLite DB
├── .gitignore              # Files/folders to exclude from Git
└── README.md               # Project overview
```

---

## ⚙️ Setup Instructions

### 1. 📥 Clone the Repository
```bash
git clone https://github.com/paaveenya/student-feedback-system.git
cd student-feedback-system
```

### 2. 🧱 Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate   # For Windows
```

### 3. 📦 Install Dependencies
```bash
pip install -r requirements.txt
```
(Note: You'll need to manually create `requirements.txt` if not yet present.)

### 4. ⚙️ Initialize DB & Create Users
```bash
python add_users.py
```
This creates `admin/admin123` and `student/student123` users.

### 5. 🚀 Run the App
```bash
python app.py
```
Access it at [http://localhost:5000](http://localhost:5000)

---

## 📸 Screenshots
*(Optional: You can paste screenshots of admin dashboard, student feedback form, etc.)*

---

## 📌 Notes
- Default credentials:
  - Admin: `admin` / `admin123`
  - Student: `student` / `student123`
- You can add subjects and questions before students start feedback.
- Sections like IT-A or IT-B help organize responses.

---


