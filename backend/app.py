from fastapi import FastAPI
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from analytics import process_student_data

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all domains
    allow_credentials=True,
    allow_methods=["*"],   # allow all methods (GET, POST, etc)
    allow_headers=["*"],   # allow all headers
)

# Simple in-memory storage
students_db = []

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

@app.get("/")
def root():
    return {"message": "API is working"}

@app.get("/students")
def get_students():
    return students_db

@app.get("/students/performance-summary")
def get_performance_summary():
    if not students_db:
        return {
            "total_students": 0,
            "category_counts": {},
            "at_risk_count": 0,
            "top_10_percent_students": []
        }
    
    # Calculate category counts
    category_counts = {}
    for student in students_db:
        category = student['category']
        category_counts[category] = category_counts.get(category, 0) + 1
    
    # Calculate at-risk count
    at_risk_count = sum(1 for student in students_db if student['is_at_risk'])
    
    # Get top 10% students
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)