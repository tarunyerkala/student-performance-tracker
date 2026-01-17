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
        const response = await fetch(`${API_BASE_URL}/students`, {
            cache: "no-store"
        });

        allStudents = await response.json();
        filteredStudents = [...allStudents];

        updateStudentList();
        updateTotalCount();
        await loadSummary();


        document.getElementById("studentId").value = generateNextStudentId();

    } catch (error) {
        showError('Failed to load data.');
        console.error(error);
    }
}



// Load performance summary
async function loadSummary() {
    try {
        console.log("Fetching summary from:", `${API_BASE_URL}/students/performance-summary`);

        const response = await fetch(`${API_BASE_URL}/students/performance-summary`);

        console.log("Response status:", response.status, response.statusText);

        if (!response.ok) {
            const errorText = await response.text();
            console.error("Error response:", errorText);
            throw new Error(`Failed to fetch summary: ${response.status} ${response.statusText}`);
        }

        const summary = await response.json();
        console.log("Summary data received:", summary);

        renderSummary(summary);

    } catch (error) {
        console.error('Error loading summary:', error);
        // Show error on page
        summaryEl.innerHTML = `
            <div class="error-state">
                <p>Failed to load summary: ${error.message}</p>
                <p>Make sure backend is running on http://localhost:8000</p>
            </div>
        `;
    }
}

// Render summary cards
function renderSummary(summary) {
    console.log("Summary data received:", summary);

    const { total_students, category_counts, at_risk_count, top_10_percent_students } = summary;

    // Create HTML string
    const html = `
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

    console.log("Generated HTML:", html);

    // Set the HTML
    summaryEl.innerHTML = html;

    console.log("Element after update:", summaryEl.innerHTML);
}

// Update student list
function updateStudentList() {
    totalCountEl.textContent = filteredStudents.length;

    if (filteredStudents.length === 0) {
        studentListEl.innerHTML = `
            <tr>
                <td colspan="7" class="empty-state">
                    No students found matching the filters.
                </td>
            </tr>
        `;
        return;
    }

    studentListEl.innerHTML = filteredStudents.map(student => `
        <tr class="${student.is_at_risk ? 'row-risk' : ''}">
            <td class="student-id">${student.student_id}</td>
            <td>${student.name}</td>
            <td>${student.program}</td>
            <td>${student.attendance_percentage}%</td>
            <td>${student.final_score}</td>
            <td>
                <span class="badge badge-${student.category.toLowerCase().replace(' ', '-')}">
                    ${student.category}
                </span>
            </td>
            <td class="${student.is_at_risk ? 'text-danger' : 'text-success'}">
                ${student.is_at_risk ? 'Yes' : 'No'}
            </td>
        </tr>
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
        attendance_percentage: Number(document.getElementById('attendance').value),
        assignment_1: Number(document.getElementById('assignment1').value),
        assignment_2: Number(document.getElementById('assignment2').value),
        assignment_3: Number(document.getElementById('assignment3').value),
        quiz_1: Number(document.getElementById('quiz1').value),
        quiz_2: Number(document.getElementById('quiz2').value),
        midterm_score: Number(document.getElementById('midterm').value),
        final_exam_score: Number(document.getElementById('finalExam').value)
    };

    // Validate fields
    for (const [key, value] of Object.entries(studentData)) {
        if (value === "" || value === null || isNaN(value) && key !== "name" && key !== "program" && key !== "student_id") {
            showFormMessage('Please fill in all fields correctly', 'error');
            return;
        }
    }

    try {
        const response = await fetch(`${API_BASE_URL}/students`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(studentData)
        });

        const result = await response.json();

        if (response.ok) {
            showFormMessage('Student added successfully!', 'success');
            addStudentForm.reset();

            setTimeout(() => {
                loadData();   // reload + auto-generate new ID
            }, 300);
        }
        else {
            showFormMessage(result.detail || 'Failed to add student', 'error');
        }

    } catch (error) {
        console.error('Error adding student:', error);
        showFormMessage('Failed to connect to server', 'error');
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
// function showLoading() {
//     studentListEl.innerHTML = `
//         <div class="loading">
//             <p>Loading data...</p>
//         </div>
//     `;
//     summaryEl.innerHTML = `
//         <div class="loading">
//             <p>Loading summary...</p>
//         </div>
//     `;
// }

// Show error message
function showError(message) {
    studentListEl.innerHTML = `
        <div class="error-state">
            <p>${message}</p>
            <button onclick="loadData()">Retry</button>
        </div>
    `;
}

function generateNextStudentId() {
    if (allStudents.length === 0) {
        return "S001";
    }

    // Extract numeric part from student IDs
    const maxId = Math.max(
        ...allStudents.map(s =>
            parseInt(s.student_id.replace("S", ""), 10)
        )
    );

    const nextId = maxId + 1;

    // Pad with zeros → S001, S012, S123
    return `S${String(nextId).padStart(3, "0")}`;
}



function allowOnlyAlphabet(event) {
    const char = event.key;

    // Allow letters (A-Z, a-z) and space
    if (/^[a-zA-Z ]$/.test(char)) {
        return true;
    }

    // Allow control keys (Backspace, Delete, Arrow keys)
    if (
        event.key === "Backspace" ||
        event.key === "Delete" ||
        event.key === "ArrowLeft" ||
        event.key === "ArrowRight" ||
        event.key === "Tab"
    ) {
        return true;
    }

    event.preventDefault();
    return false;
}

function allowOnlyNumber(event) {
    const char = event.key;
    const input = event.target.value;

    // Allow digits
    if (char >= '0' && char <= '9') {
        return true;
    }

    // Allow only ONE decimal point
    if (char === '.' && !input.includes('.')) {
        return true;
    }

    // Allow control keys
    if (
        event.key === "Backspace" ||
        event.key === "Delete" ||
        event.key === "ArrowLeft" ||
        event.key === "ArrowRight" ||
        event.key === "Tab"
    ) {
        return true;
    }

    event.preventDefault();
    return false;
}
