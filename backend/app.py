from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import pandas as pd
import json
import os
from analytics import process_student_data, generate_reports, get_top_10_percent_students

app = FastAPI(title="Student Performance Tracker API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Frontend server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
students_db = []

# Load initial data from CSV
def load_initial_data():
    """Load initial student data from CSV"""
    global students_db
    try:
        df = process_student_data()
        students_db = df.to_dict('records')
        print(f"Loaded {len(students_db)} students from CSV")
    except Exception as e:
        print(f"Error loading initial data: {e}")
        students_db = []

# Pydantic models
class StudentCreate(BaseModel):
    student_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    program: str = Field(..., min_length=1)
    attendance_percentage: float = Field(..., ge=0, le=100)
    assignment_1: float = Field(..., ge=0, le=100)
    assignment_2: float = Field(..., ge=0, le=100)
    assignment_3: float = Field(..., ge=0, le=100)
    quiz_1: float = Field(..., ge=0, le=100)
    quiz_2: float = Field(..., ge=0, le=100)
    midterm_score: float = Field(..., ge=0, le=100)
    final_exam_score: float = Field(..., ge=0, le=100)

class StudentResponse(BaseModel):
    student_id: str
    name: str
    program: str
    attendance_percentage: float
    final_score: float
    category: str
    is_at_risk: bool

class SummaryResponse(BaseModel):
    total_students: int
    category_counts: Dict[str, int]
    at_risk_count: int
    top_10_percent_students: List[str]

# Helper functions
def calculate_student_metrics(student: dict) -> dict:
    """Calculate metrics for a student"""
    # Calculate averages
    assignment_avg = round((student['assignment_1'] + student['assignment_2'] + student['assignment_3']) / 3, 2)
    quiz_avg = round((student['quiz_1'] + student['quiz_2']) / 2, 2)
    
    # Calculate final score
    final_score = round(
        assignment_avg * 0.30 +
        quiz_avg * 0.20 +
        student['midterm_score'] * 0.20 +
        student['final_exam_score'] * 0.30, 2
    )
    
    # Determine category
    if final_score >= 85:
        category = "Excellent"
    elif final_score >= 70:
        category = "Good"
    else:
        category = "Needs Improvement"
    
    # Determine at-risk status
    is_at_risk = student['attendance_percentage'] < 60 or final_score < 65
    
    return {
        "assignment_avg": assignment_avg,
        "quiz_avg": quiz_avg,
        "final_score": final_score,
        "category": category,
        "is_at_risk": is_at_risk
    }

# Load initial data on startup
load_initial_data()

@app.get("/")
def read_root():
    return {"message": "Student Performance Tracker API", "docs": "/docs"}

@app.post("/students", response_model=Dict[str, Any])
def add_student(student: StudentCreate):
    """Add a new student"""
    # Check if student_id already exists
    if any(s['student_id'] == student.student_id for s in students_db):
        raise HTTPException(status_code=400, detail="Student ID already exists")
    
    # Convert to dict
    student_dict = student.dict()
    
    # Calculate metrics
    metrics = calculate_student_metrics(student_dict)
    student_dict.update(metrics)
    
    # Add to database
    students_db.append(student_dict)
    
    # Regenerate reports
    generate_reports()
    
    return {
        "message": "Student added successfully",
        "student_id": student.student_id
    }

@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: str):
    """Get student by ID"""
    for student in students_db:
        if student['student_id'] == student_id:
            return StudentResponse(
                student_id=student['student_id'],
                name=student['name'],
                program=student['program'],
                attendance_percentage=student['attendance_percentage'],
                final_score=student['final_score'],
                category=student['category'],
                is_at_risk=student['is_at_risk']
            )
    
    raise HTTPException(status_code=404, detail="Student not found")

@app.get("/students", response_model=List[StudentResponse])
def get_students(
    category: Optional[str] = Query(None, description="Filter by category"),
    at_risk: Optional[bool] = Query(None, description="Filter by at-risk status")
):
    """Get all students with optional filters"""
    filtered_students = students_db
    
    # Apply filters
    if category:
        filtered_students = [s for s in filtered_students if s['category'] == category]
    
    if at_risk is not None:
        filtered_students = [s for s in filtered_students if s['is_at_risk'] == at_risk]
    
    # Convert to response model
    return [
        StudentResponse(
            student_id=s['student_id'],
            name=s['name'],
            program=s['program'],
            attendance_percentage=s['attendance_percentage'],
            final_score=s['final_score'],
            category=s['category'],
            is_at_risk=s['is_at_risk']
        )
        for s in filtered_students
    ]

@app.get("/students/performance-summary", response_model=SummaryResponse)
def get_performance_summary():
    """Get performance summary"""
    if not students_db:
        return SummaryResponse(
            total_students=0,
            category_counts={},
            at_risk_count=0,
            top_10_percent_students=[]
        )
    
    # Calculate category counts
    category_counts = {}
    for student in students_db:
        category = student['category']
        category_counts[category] = category_counts.get(category, 0) + 1
    
    # Calculate at-risk count
    at_risk_count = sum(1 for student in students_db if student['is_at_risk'])
    
    # Get top 10% students
    df = pd.DataFrame(students_db)
    top_10_percent = get_top_10_percent_students(df)
    
    return SummaryResponse(
        total_students=len(students_db),
        category_counts=category_counts,
        at_risk_count=at_risk_count,
        top_10_percent_students=top_10_percent
    )

@app.get("/students/full/{student_id}")
def get_student_full_details(student_id: str):
    """Get complete student details including all scores"""
    for student in students_db:
        if student['student_id'] == student_id:
            return student
    
    raise HTTPException(status_code=404, detail="Student not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)