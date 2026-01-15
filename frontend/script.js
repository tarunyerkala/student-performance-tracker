const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const studentListEl = document.getElementById('studentList');
const totalCountEl = document.getElementById('totalCount');
const summaryEl = document.getElementById('summary');
const categoryFilter = document.getElementById('categoryFilter');
const atRiskFilter = document.getElementById('atRiskFilter');
const applyFiltersBtn = document.getElementById('applyFilters');
const resetFiltersBtn = document.getElementById('resetFilters');
const refreshBtn = document.getElementById('refreshBtn');
const addStudentForm = document.getElementById('addStudentForm');
const formMessage = document.getElementById('formMessage');

// State
let allStudents = [];
let filteredStudents = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadData();
    
    // Event Listeners
    applyFiltersBtn.addEventListener('click', applyFilters);
    resetFiltersBtn.addEventListener('click', resetFilters);
    refreshBtn.addEventListener('click', loadData);
    addStudentForm.addEventListener('submit', handleAddStudent);
});

// Load all data
async function loadData() {
    try {
        showLoading();
        
        // Load students
        const response = await fetch(`${API_BASE_URL}/students`);
        if (!response.ok) throw new Error('Failed to fetch students');
        
        allStudents = await response.json();
        filteredStudents = [...allStudents];
        
        // Load summary
        await loadSummary();
        
        // Update display
        updateStudentList();
        updateTotalCount();
        
    } catch (error) {
        showError('Failed to load data. Make sure backend is running on port 8000.');
        console.error('Error loading data:', error);
    }
}

// Load performance summary
async function loadSummary() {
    try {
        const response = await fetch(`${API_BASE_URL}/students/performance-summary`);
        if (!response.ok) throw new Error('Failed to fetch summary');
        
        const summary = await response.json();
        renderSummary(summary);
        
    } catch (error) {
        console.error('Error loading summary:', error);
    }
}

// Render summary cards
function renderSummary(summary) {
    const { total_students, category_counts, at_risk_count, top_10_percent_students } = summary;
    
    summaryEl.innerHTML = `
        <div class="summary-card">
            <h3>Total Students</h3>
            <div class="value">${total_students}</div>
            <div class="label">Registered Students</div>
        </div>
        <div class="summary-card">
            <h3>Excellent Students</h3>
            <div class="value">${category_counts.Excellent || 0}</div>
            <div class="label">Score ≥ 85</div>
        </div>
        <div class="summary-card">
            <h3>At-Risk Students</h3>
            <div class="value">${at_risk_count}</div>
            <div class="label">Need Attention</div>
        </div>
        <div class="summary-card">
            <h3>Top Performers</h3>
            <div class="value">${top_10_percent_students.length}</div>
            <div class="label">Top 10%</div>
        </div>
    `;
}

// Update student list
function updateStudentList() {
    if (filteredStudents.length === 0) {
        studentListEl.innerHTML = `
            <div class="empty-state">
                <p>No students found matching the filters.</p>
            </div>
        `;
        return;
    }
    
    studentListEl.innerHTML = filteredStudents.map(student => `
        <div class="student-card ${student.category.toLowerCase().replace(' ', '-')} ${student.is_at_risk ? 'at-risk' : ''}">
            <div class="student-header">
                <div class="student-id">${student.student_id}</div>
                <div class="category-badge category-${student.category.toLowerCase().replace(' ', '-')}">
                    ${student.category}
                </div>
            </div>
            <div class="student-name">${student.name}</div>
            <div class="student-program">${student.program}</div>
            
            <div class="student-metrics">
                <div class="metric">
                    <div class="metric-label">Attendance</div>
                    <div class="metric-value">${student.attendance_percentage}%</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Final Score</div>
                    <div class="metric-value">${student.final_score}</div>
                </div>
            </div>
            
            ${student.is_at_risk ? `
                <div class="at-risk-badge">
                    ⚠️ At Risk
                </div>
            ` : ''}
        </div>
    `).join('');
}

// Update total count
function updateTotalCount() {
    totalCountEl.textContent = filteredStudents.length;
}

// Apply filters
function applyFilters() {
    let filtered = [...allStudents];
    
    // Apply category filter
    const category = categoryFilter.value;
    if (category) {
        filtered = filtered.filter(student => student.category === category);
    }
    
    // Apply at-risk filter
    if (atRiskFilter.checked) {
        filtered = filtered.filter(student => student.is_at_risk);
    }
    
    filteredStudents = filtered;
    updateStudentList();
    updateTotalCount();
}

// Reset filters
function resetFilters() {
    categoryFilter.value = '';
    atRiskFilter.checked = false;
    filteredStudents = [...allStudents];
    updateStudentList();
    updateTotalCount();
}

// Handle add student form submission
async function handleAddStudent(e) {
    e.preventDefault();
    
    const studentData = {
        student_id: document.getElementById('studentId').value.trim(),
        name: document.getElementById('studentName').value.trim(),
        program: document.getElementById('program').value.trim(),
        attendance_percentage: parseFloat(document.getElementById('attendance').value),
        assignment_1: parseFloat(document.getElementById('assignment1').value),
        assignment_2: parseFloat(document.getElementById('assignment2').value),
        assignment_3: parseFloat(document.getElementById('assignment3').value),
        quiz_1: parseFloat(document.getElementById('quiz1').value),
        quiz_2: parseFloat(document.getElementById('quiz2').value),
        midterm_score: parseFloat(document.getElementById('midterm').value),
        final_exam_score: parseFloat(document.getElementById('finalExam').value)
    };
    
    // Validate all fields are filled
    for (const [key, value] of Object.entries(studentData)) {
        if (value === undefined || (typeof value === 'number' && isNaN(value))) {
            showFormMessage('Please fill in all fields correctly', 'error');
            return;
        }
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/students`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(studentData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showFormMessage('Student added successfully!', 'success');
            addStudentForm.reset();
            
            // Reload data to show new student
            setTimeout(() => {
                loadData();
                resetFilters();
            }, 1000);
            
        } else {
            showFormMessage(result.detail || 'Failed to add student', 'error');
        }
        
    } catch (error) {
        showFormMessage('Failed to connect to server', 'error');
        console.error('Error adding student:', error);
    }
}

// Show form message
function showFormMessage(message, type) {
    formMessage.textContent = message;
    formMessage.className = `message ${type}`;
    
    setTimeout(() => {
        formMessage.textContent = '';
        formMessage.className = 'message';
    }, 3000);
}

// Show loading state
function showLoading() {
    studentListEl.innerHTML = `
        <div class="loading">
            <p>Loading data...</p>
        </div>
    `;
    summaryEl.innerHTML = `
        <div class="loading">
            <p>Loading summary...</p>
        </div>
    `;
}

// Show error message
function showError(message) {
    studentListEl.innerHTML = `
        <div class="error-state">
            <p>${message}</p>
            <button onclick="loadData()">Retry</button>
        </div>
    `;
}