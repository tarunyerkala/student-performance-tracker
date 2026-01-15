import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from analytics import process_student_data, generate_reports
from app import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_empty_csv():
    """Test with empty CSV"""
    # Create temporary empty CSV
    empty_df = pd.DataFrame(columns=[
        'student_id', 'name', 'program', 'attendance_percentage',
        'assignment_1', 'assignment_2', 'assignment_3',
        'quiz_1', 'quiz_2', 'midterm_score', 'final_exam_score'
    ])
    
    empty_df.to_csv('test_empty.csv', index=False)
    
    try:
        # Test analytics functions with empty data
        df = pd.read_csv('test_empty.csv')
        assert len(df) == 0
        
        # Test summary with empty data
        response = client.get("/students/performance-summary")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_students"] == 0
        assert data["at_risk_count"] == 0
        assert data["top_10_percent_students"] == []
        
    finally:
        # Cleanup
        if os.path.exists('test_empty.csv'):
            os.remove('test_empty.csv')

def test_invalid_score_values():
    """Test validation of score values"""
    invalid_student = {
        "student_id": "INVALID001",
        "name": "Invalid Student",
        "program": "Test",
        "attendance_percentage": 150,  # Invalid: > 100
        "assignment_1": -10,  # Invalid: < 0
        "assignment_2": 85.0,
        "assignment_3": 90.0,
        "quiz_1": 75.0,
        "quiz_2": 80.0,
        "midterm_score": 85.0,
        "final_exam_score": 90.0
    }
    
    response = client.post("/students", json=invalid_student)
    # Should return 422 for validation error
    assert response.status_code == 422

def test_missing_student_id():
    """Test missing student_id validation"""
    incomplete_student = {
        "name": "No ID Student",
        "program": "Test",
        "attendance_percentage": 85.0,
        "assignment_1": 80.0,
        "assignment_2": 85.0,
        "assignment_3": 90.0,
        "quiz_1": 75.0,
        "quiz_2": 80.0,
        "midterm_score": 85.0,
        "final_exam_score": 90.0
        # Missing student_id
    }
    
    response = client.post("/students", json=incomplete_student)
    assert response.status_code == 422  # Validation error

def test_boundary_values():
    """Test boundary values for scores"""
    # Test minimum valid values
    min_student = {
        "student_id": "BOUNDARY001",
        "name": "Min Student",
        "program": "Test",
        "attendance_percentage": 0.0,
        "assignment_1": 0.0,
        "assignment_2": 0.0,
        "assignment_3": 0.0,
        "quiz_1": 0.0,
        "quiz_2": 0.0,
        "midterm_score": 0.0,
        "final_exam_score": 0.0
    }
    
    response = client.post("/students", json=min_student)
    assert response.status_code == 200
    
    # Test maximum valid values
    max_student = {
        "student_id": "BOUNDARY002",
        "name": "Max Student",
        "program": "Test",
        "attendance_percentage": 100.0,
        "assignment_1": 100.0,
        "assignment_2": 100.0,
        "assignment_3": 100.0,
        "quiz_1": 100.0,
        "quiz_2": 100.0,
        "midterm_score": 100.0,
        "final_exam_score": 100.0
    }
    
    response = client.post("/students", json=max_student)
    assert response.status_code == 200

def test_decimal_scores():
    """Test decimal score values"""
    decimal_student = {
        "student_id": "DECIMAL001",
        "name": "Decimal Student",
        "program": "Test",
        "attendance_percentage": 87.5,
        "assignment_1": 89.5,
        "assignment_2": 92.5,
        "assignment_3": 88.5,
        "quiz_1": 85.5,
        "quiz_2": 90.5,
        "midterm_score": 87.5,
        "final_exam_score": 92.5
    }
    
    response = client.post("/students", json=decimal_student)
    assert response.status_code == 200

def test_special_characters():
    """Test names with special characters"""
    special_student = {
        "student_id": "SPECIAL001",
        "name": "Élève Français & Español",
        "program": "International Studies",
        "attendance_percentage": 85.0,
        "assignment_1": 80.0,
        "assignment_2": 85.0,
        "assignment_3": 90.0,
        "quiz_1": 75.0,
        "quiz_2": 80.0,
        "midterm_score": 85.0,
        "final_exam_score": 90.0
    }
    
    response = client.post("/students", json=special_student)
    assert response.status_code == 200

if __name__ == "__main__":
    test_empty_csv()
    test_invalid_score_values()
    test_missing_student_id()
    test_boundary_values()
    test_decimal_scores()
    test_special_characters()
    print("All edge case tests passed! ✅")