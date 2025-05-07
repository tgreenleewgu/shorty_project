# ShortyURL Backend Guide

## Overview
This guide walks you through setting up and maintaining the **ShortyURL** backend application. The backend is built with Django REST Framework and connects to MongoDB Atlas.

## ⚙️ System Requirements
* **Python:** 3.11+
* **MongoDB Atlas:** cloud-hosted database
* **Git:** for version control

## 🛠️ Backend Setup

### 1. Clone the Repository
```bash
git clone https://github.com/tgreenleewgu/shorty_project.git
cd shortyurl
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
.\venv\Scripts\activate         # Windows
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root folder:
```
SECRET_KEY=your-django-secret-key
MONGODB_URI=your-mongodb-connection-string
```

### 5. Run Migrations and Unit Tests
```bash
python manage.py migrate
python manage.py test
```

### 6. Start the Development Server
```bash
python manage.py runserver
```
