from fastapi import FastAPI, HTTPException
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from analytics import process_student_data

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
students_db = []


# -------------------------------
# Student Schema
# -------------------------------
class Student(BaseModel):
    student_id: str
    name: str
    program: str
    attendance_percentage: float
    assignment_1: float
    assignment_2: float
    assignment_3: float
    quiz_1: float
    quiz_2: float
    midterm_score: float
    final_exam_score: float


# -------------------------------
# Load students on startup
# -------------------------------
@app.on_event("startup")
def startup():
    global students_db
    try:
        df = process_student_data()
        students_db = df.to_dict('records')
        print(f"✓ Loaded {len(students_db)} students")
    except Exception as e:
        print(f"✗ Error: {e}")
        students_db = []


# -------------------------------
# Root API
# -------------------------------
@app.get("/")
def root():
    return {"message": "API is working"}


# -------------------------------
# Get all students
# -------------------------------
@app.get("/students")
def get_students():
    return students_db


# -------------------------------
# Insert new student
# -------------------------------
@app.post("/students")
def add_student(student: Student):
    # Check for duplicate student_id
    for s in students_db:
        if s["student_id"] == student.student_id:
            raise HTTPException(status_code=400, detail="Student ID already exists")

    student_dict = student.dict()

    # Optional: calculate final score (example)
    student_dict["final_score"] = round(
        (
            student.assignment_1 +
            student.assignment_2 +
            student.assignment_3 +
            student.quiz_1 +
            student.quiz_2 +
            student.midterm_score +
            student.final_exam_score
        ) / 7, 2
    )

    # Optional: category logic
    if student_dict["final_score"] >= 85:
        student_dict["category"] = "Excellent"
    elif student_dict["final_score"] >= 70:
        student_dict["category"] = "Good"
    elif student_dict["final_score"] >= 50:
        student_dict["category"] = "Average"
    else:
        student_dict["category"] = "Poor"

    student_dict["is_at_risk"] = student_dict["final_score"] < 50

    students_db.append(student_dict)

    return {
        "message": "Student added successfully",
        "student": student_dict
    }


# -------------------------------
# Performance Summary API
# -------------------------------
@app.get("/students/performance-summary")
def get_performance_summary():
    if not students_db:
        return {
            "total_students": 0,
            "category_counts": {},
            "at_risk_count": 0,
            "top_10_percent_students": []
        }

    category_counts = {}
    for student in students_db:
        category = student.get('category', 'Unknown')
        category_counts[category] = category_counts.get(category, 0) + 1

    at_risk_count = sum(1 for student in students_db if student.get('is_at_risk'))

    df = pd.DataFrame(students_db)
    if len(df) > 0:
        sorted_df = df.sort_values('final_score', ascending=False)
        top_count = max(1, int(len(sorted_df) * 0.1))
        top_10_percent = sorted_df.head(top_count)['student_id'].tolist()
    else:
        top_10_percent = []

    return {
        "total_students": len(students_db),
        "category_counts": category_counts,
        "at_risk_count": at_risk_count,
        "top_10_percent_students": top_10_percent
    }


# -------------------------------
# Run server
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
