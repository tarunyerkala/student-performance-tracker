import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_get_students():
    """Test GET /students endpoint"""
    response = client.get("/students")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_performance_summary():
    """Test GET /students/performance-summary endpoint"""
    response = client.get("/students/performance-summary")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_students" in data
    assert "category_counts" in data
    assert "at_risk_count" in data
    assert "top_10_percent_students" in data

def test_get_student_by_id():
    """Test GET /students/{id} endpoint"""
    response = client.get("/students/S001")
    assert response.status_code == 200
    
    data = response.json()
    assert data["student_id"] == "S001"
    assert "name" in data
    assert "final_score" in data
    assert "category" in data
    assert "is_at_risk" in data

def test_get_nonexistent_student():
    """Test GET /students/{id} with non-existent ID"""
    response = client.get("/students/INVALID_ID")
    assert response.status_code == 404

def test_add_student():
    """Test POST /students endpoint"""
    student_data = {
        "student_id": "TEST001",
        "name": "Test Student",
        "program": "Test Program",
        "attendance_percentage": 85.0,
        "assignment_1": 80.0,
        "assignment_2": 85.0,
        "assignment_3": 90.0,
        "quiz_1": 75.0,
        "quiz_2": 80.0,
        "midterm_score": 85.0,
        "final_exam_score": 90.0
    }
    
    response = client.post("/students", json=student_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["message"] == "Student added successfully"
    assert data["student_id"] == "TEST001"
    
    # Clean up - verify we can get the added student
    response = client.get("/students/TEST001")
    assert response.status_code == 200

def test_add_duplicate_student():
    """Test adding duplicate student"""
    student_data = {
        "student_id": "S001",  # Already exists
        "name": "Duplicate",
        "program": "Test",
        "attendance_percentage": 85.0,
        "assignment_1": 80.0,
        "assignment_2": 85.0,
        "assignment_3": 90.0,
        "quiz_1": 75.0,
        "quiz_2": 80.0,
        "midterm_score": 85.0,
        "final_exam_score": 90.0
    }
    
    response = client.post("/students", json=student_data)
    assert response.status_code == 400

def test_filter_students_by_category():
    """Test filtering students by category"""
    response = client.get("/students?category=Excellent")
    assert response.status_code == 200
    
    students = response.json()
    if students:
        for student in students:
            assert student["category"] == "Excellent"

def test_filter_students_by_at_risk():
    """Test filtering students by at-risk status"""
    response = client.get("/students?at_risk=true")
    assert response.status_code == 200
    
    students = response.json()
    if students:
        for student in students:
            assert student["is_at_risk"] == True

if __name__ == "__main__":
    test_root_endpoint()
    test_get_students()
    test_get_performance_summary()
    test_get_student_by_id()
    test_get_nonexistent_student()
    test_add_student()
    test_add_duplicate_student()
    test_filter_students_by_category()
    test_filter_students_by_at_risk()
    print("All API tests passed! ✅")