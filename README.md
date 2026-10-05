# 🎓 E-Learning Platform

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-green.svg)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)

A comprehensive **E-Learning Platform** built with Django that enables instructors to create courses and students to learn at their own pace.

## ✨ Features
### For Students
- 📝 User registration and authentication
- 📚 Browse and search courses by category
- 🎥 Stream video lectures
- ✅ Track course progress
- 📊 View completion certificates
- ⭐ Rate and review courses



### Admin Features
- 👑 User management (students/instructors)
- 📋 Course approval workflow
- 🔔 System announcements
- 📊 Analytics dashboard
- 💵 Payment management (if applicable)

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- PostgreSQL (optional, SQLite works for development)
- Git

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/suyog123-hub/E-learning-platform.git
cd E-learning-platform

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 4. Install dependencies (from the project root)
pip install -r learning/requirements.txt

# 5. Configure environment
# Copy learning/.env.example to learning/.env and fill in your secrets
# (SECRET_KEY, EMAIL_*, GOOGLE_OAUTH2_*, ESEWA_SECRET_KEY)

# 6. Run database migrations (from the learning/ directory)
cd learning
python manage.py migrate

# 7. Create superuser (admin account)
python manage.py createsuperuser

python manage.py runserver
