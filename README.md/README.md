# Student Performance Tracker

A full-stack application for managing and analyzing student academic performance using CSV data processing, FastAPI, and a web-based dashboard.



 Overview
The Student Performance Tracker helps institutions analyze academic performance, identify at-risk students, and visualize results through an interactive dashboard.

Key capabilities:
- CSV-based data ingestion
- Automated score calculations
- RESTful APIs
- Interactive frontend dashboard
- Comprehensive test suite



 Architecture Overview

Data Flow:

CSV → Python Analytics → FastAPI → Frontend Dashboard


System Components:
- Analytics Engine (Python + Pandas)
- REST API (FastAPI)
- Web Dashboard (HTML, CSS, JavaScript)
- Test Suite (Pytest)



 Project Structure

student-performance-tracker/
│
├── backend/
│   ├── app.py                     # FastAPI application
│   ├── analytics.py               # Data processing logic
│   ├── models.py                  # Pydantic models
│   ├── database.py                # Data storage layer
│   ├── requirements.txt           # Python dependencies
│   ├── students.csv               # Initial dataset
│   └── generated_outputs/
│       ├── students_report.csv    # Processed student data
│       └── summary_report.json    # Aggregated statistics
│
├── frontend/
│   ├── index.html                 # Dashboard UI
│   ├── style.css                  # Styling
│   └── script.js                  # Frontend logic
│
├── tests/
│   ├── test_calculations.py       # Calculation tests
│   ├── test_api.py                # API tests
│   ├── test_edge_cases.py         # Edge case tests
│   └── conftest.py                # Pytest fixtures
│
└── README.md                      # Project documentation




 Installation

# Prerequisites
- Python 3.8 or higher
- Modern web browser
- Git (optional)

# Setup Instructions
1. Navigate to the backend directory:
bash
cd student-performance-tracker/backend


2. Create a virtual environment:
bash
python -m venv venv


3. Activate the virtual environment:
- Windows:
bash
venv\Scripts\activate

- macOS/Linux:
bash
source venv/bin/activate


4. Install dependencies:
bash
pip install -r requirements.txt




 Dependencies
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- pytest==7.4.3
- pandas==2.1.3
- httpx==0.25.1



 Running the Application

# Phase 1: Data Processing
bash
python analytics.py

Expected output:
- students_report.csv generated
- summary_report.json generated



# Phase 2: Start Backend API
bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000


Access URLs:
- API Base: http://127.0.0.1:8000
- Swagger Docs: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc



# Phase 3: Launch Dashboard

Option A: Open directly
- Open frontend/index.html in a browser

Option B: Using local server
bash
cd frontend
python -m http.server 8080

Access at http://localhost:8080



 API Documentation

# Base URL

http://127.0.0.1:8000


# Endpoints
| Method | Endpoint | Description |
||--||
| POST | /students | Add a new student |
| GET | /students | List students |
| GET | /students/{student_id} | Get student details |
| GET | /students/performance-summary | Performance statistics |



# POST /students

Adds a new student record.

Request body:
json
{
  "student_id": "S009",
  "name": "New Student",
  "program": "B.Tech",
  "attendance_percentage": 78,
  "assignment_1": 80,
  "assignment_2": 70,
  "assignment_3": 90,
  "quiz_1": 85,
  "quiz_2": 88,
  "midterm_score": 75,
  "final_exam_score": 80
}




 Testing

Run all tests:
bash
python -m pytest tests/ -v


Test coverage:
bash
pytest --cov=. tests/


Test categories:
- Calculation tests
- API tests
- Edge case tests



 Dashboard Features
- Student list with computed metrics
- Performance summary statistics
- Filtering by category and risk status
- Responsive design



 Calculation Rules

Assignment Average:

(assignment_1 + assignment_2 + assignment_3) / 3


Quiz Average:

(quiz_1 + quiz_2) / 2


Final Score:

(assignment_avg * 0.30)
+ (quiz_avg * 0.20)
+ (midterm_score * 0.20)
+ (final_exam_score * 0.30)




 Performance Categories
- Excellent: final_score >= 85
- Good: 70 <= final_score < 85
- Needs Improvement: final_score < 70



 At-Risk Criteria
A student is considered at-risk if:
- attendance_percentage < 60
- final_score < 65



 Troubleshooting
- Port already in use: change the port number
- CSV not found: run analytics.py from backend directory
- CORS issues: verify backend is running and API URL is correct



 Deployment

Development:
bash
uvicorn app:app --reload


Production:
bash
uvicorn app:app --host 0.0.0.0 --port 80 --workers 4


