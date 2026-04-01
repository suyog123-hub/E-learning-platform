# 🎓 E-Learning Platform

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1-green.svg)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)

A comprehensive **E-Learning Platform** built with Django that enables instructors to create courses and students to learn at their own pace.

## ✨ Features

### For Students
- 📝 User registration and authentication
- 📚 Browse and search courses by category
- 🎥 Stream video lectures
- ✅ Track course progress
- 📊 View completion certificates
- 💬 Participate in discussion forums
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

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up database
python manage.py migrate

# 6. Create superuser (admin account)
python manage.py createsuperuser

# 7. Run development server
python manage.py runserver
