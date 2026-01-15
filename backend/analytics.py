import pandas as pd
import json
import os
from typing import Dict, List, Any

def calculate_assignment_avg(row: pd.Series) -> float:
    """Calculate assignment average"""
    return round((row['assignment_1'] + row['assignment_2'] + row['assignment_3']) / 3, 2)

def calculate_quiz_avg(row: pd.Series) -> float:
    """Calculate quiz average"""
    return round((row['quiz_1'] + row['quiz_2']) / 2, 2)

def calculate_final_score(row: pd.Series, assignment_avg: float, quiz_avg: float) -> float:
    """Calculate final weighted score"""
    final_score = (
        assignment_avg * 0.30 +
        quiz_avg * 0.20 +
        row['midterm_score'] * 0.20 +
        row['final_exam_score'] * 0.30
    )
    return round(final_score, 2)

def determine_category(final_score: float) -> str:
    """Determine performance category"""
    if final_score >= 85:
        return "Excellent"
    elif final_score >= 70:
        return "Good"
    else:
        return "Needs Improvement"

def determine_at_risk(attendance: float, final_score: float) -> bool:
    """Determine if student is at-risk"""
    return attendance < 60 or final_score < 65

def get_top_10_percent_students(df: pd.DataFrame) -> List[str]:
    """Get top 10% students by final_score"""
    if df.empty:
        return []
    
    # Sort by final_score descending
    sorted_df = df.sort_values('final_score', ascending=False)
    
    # Calculate top 10%
    total_students = len(sorted_df)
    top_count = max(1, int(total_students * 0.1))  # At least 1 student
    
    # Get top student IDs
    top_students = sorted_df.head(top_count)['student_id'].tolist()
    return top_students

def process_student_data(input_file: str = "students.csv") -> pd.DataFrame:
    """Process student data and calculate metrics"""
    
    # Read CSV file
    df = pd.read_csv(input_file)
    
    # Calculate metrics
    df['assignment_avg'] = df.apply(calculate_assignment_avg, axis=1)
    df['quiz_avg'] = df.apply(calculate_quiz_avg, axis=1)
    df['final_score'] = df.apply(
        lambda row: calculate_final_score(row, row['assignment_avg'], row['quiz_avg']), 
        axis=1
    )
    df['category'] = df['final_score'].apply(determine_category)
    df['is_at_risk'] = df.apply(
        lambda row: determine_at_risk(row['attendance_percentage'], row['final_score']), 
        axis=1
    )
    
    return df

def generate_reports():
    """Generate both CSV and JSON reports"""
    
    # Ensure output directory exists
    os.makedirs("generated_outputs", exist_ok=True)
    
    # Process data
    df = process_student_data()
    
    # Generate CSV report
    csv_output_path = "generated_outputs/students_report.csv"
    df.to_csv(csv_output_path, index=False)
    print(f"CSV report generated: {csv_output_path}")
    
    # Generate JSON summary
    total_students = len(df)
    category_counts = df['category'].value_counts().to_dict()
    at_risk_count = df['is_at_risk'].sum()
    top_10_percent = get_top_10_percent_students(df)
    
    summary_data = {
        "total_students": int(total_students),
        "category_counts": category_counts,
        "at_risk_count": int(at_risk_count),
        "top_10_percent_students": top_10_percent
    }
    
    json_output_path = "generated_outputs/summary_report.json"
    with open(json_output_path, 'w') as f:
        json.dump(summary_data, f, indent=2)
    
    print(f"JSON report generated: {json_output_path}")
    
    # Print sample output for verification
    print("\nSample Student Metrics:")
    for i, row in df.head(3).iterrows():
        print(f"\n{row['student_id']} - {row['name']}:")
        print(f"  Assignment Avg: {row['assignment_avg']}")
        print(f"  Quiz Avg: {row['quiz_avg']}")
        print(f"  Final Score: {row['final_score']}")
        print(f"  Category: {row['category']}")
        print(f"  At Risk: {row['is_at_risk']}")
    
    return summary_data

if __name__ == "__main__":
    generate_reports()