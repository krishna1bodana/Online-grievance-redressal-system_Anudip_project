# Online-grievance-redressal-system_Anudip_project
Online Grievance Redressal System built using Django, HTML, CSS, JavaScript, MySQL, AJAX
# 🛡️ Online Grievance Redressal System

A full-stack, AI-enhanced platform designed to streamline public grievance submission, tracking, and resolution. This project features an **immersive glassmorphism UI**, automated workload balancing, and real-time status tracking.



## 🚀 Key Features

* **Immersive Transparency Dashboard:** A public-facing analytics hub featuring real-time data visualization using Chart.js.
* **AI Priority Analysis:** Automatically analyzes the sentiment and urgency of grievances to suggest priority levels (Low, Medium, High).
* **SLA & Auto-Escalation:** Built-in tracking for Service Level Agreements (SLA). Cases crossing the 48-hour mark are automatically flagged for escalation.
* **Officer Workload Balancing:** An intelligent assignment logic that routes cases to officers based on their current department and active caseload.
* **Glassmorphism UI:** A modern, immersive design language utilizing backdrop blurs, gradients, and micro-interactions.
* **Notification System:** Real-time in-app alerts and automated email notifications upon case resolution.



## 🛠️ Technical Stack

* **Backend:** Python 3.10+, Django 5.x
* **Database:** SQLite (Development) / PostgreSQL (Production)
* **Frontend:** Bootstrap 5, Custom CSS3 (Glassmorphism), JavaScript (ES6+)
* **Data Visualization:** Chart.js
* **AI/ML:** Scikit-learn (TF-IDF Vectorization for duplicate detection)

## 📂 Project Structure

```text
├── core/               # Project configuration (settings, urls, wsgi)
├── grievance/          # Main application logic
│   ├── models.py       # Database schema (Grievance, Officer, Notification)
│   ├── views.py        # Controller logic & API endpoints
│   ├── utils/          # AI analysis, Scrapers, and Escalation logic
│   └── forms.py        # Custom signup and grievance forms
├── templates/          # HTML5 Templates (Immersive Dashboard, Profile, etc.)
├── static/             # Immersive CSS, JS, and Images
├── manage.py           # Django command-line utility
└── requirements.txt    # Project dependencies
Installation & Setup

    Clone the Repository:
    Bash

git clone [https://github.com/krishna1bodana/Online-grievance-redressal-system_Anudip_project.git](https://github.com/krishna1bodana/Online-grievance-redressal-system_Anudip_project.git)
cd Online-grievance-redressal-system_Anudip_project

Create a Virtual Environment:
Bash

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install Dependencies:
Bash

pip install -r requirements.txt

Run Migrations:
Bash

python manage.py makemigrations
python manage.py migrate

Create an Admin User:
Bash

python manage.py createsuperuser

Start the Server:
Bash

python manage.py runserver

Access the app at http://127.0.0.1:8000/.