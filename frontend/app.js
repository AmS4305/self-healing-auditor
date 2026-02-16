// Self-Healing Code Auditor - Frontend Logic

// Determine API base URL
// If running on port 8000 (backend serving frontend), utilize relative path
// If running via Live Server (e.g., port 5500), point to backend at localhost:8000
const API_BASE = window.location.port === '8000' 
    ? '/api' 
    : 'http://localhost:8000/api';

// DOM Elements
const codeInput = document.getElementById('codeInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const clearBtn = document.getElementById('clearBtn');
const loadingDiv = document.getElementById('loading');
const resultsDiv = document.getElementById('results');
const timelineDiv = document.getElementById('timeline');
const statusBadge = document.getElementById('statusBadge');
const statusIcon = document.getElementById('statusIcon');
const statusText = document.getElementById('statusText');
const iterationCount = document.getElementById('iterationCount');

// Sample vulnerable code for demo
const SAMPLE_CODE = `# Flask API with SQL Injection vulnerability
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route('/user')
def get_user():
    user_id = request.args.get('id')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Vulnerable: Direct string interpolation
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    
    result = cursor.fetchone()
    conn.close()
    return str(result)`;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    codeInput.value = SAMPLE_CODE;
    setupEventListeners();
});

function setupEventListeners() {
    analyzeBtn.addEventListener('click', analyzeCode);
    clearBtn.addEventListener('click', clearResults);
    
    // Enable Enter key to analyze (Ctrl+Enter)
    codeInput.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            analyzeCode();
        }
    });
}

async function analyzeCode() {
    const code = codeInput.value.trim();
    
    if (!code) {
        alert('Please enter some code to analyze');
        return;
    }
    
    // Show loading state
    analyzeBtn.disabled = true;
    loadingDiv.classList.add('active');
    resultsDiv.classList.remove('active');
    
    try {
        const response = await fetch(`${API_BASE}/audit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayResults(data);
        
    } catch (error) {
        console.error('Error analyzing code:', error);
        alert(`Error: ${error.message}\n\nPlease check that:\n1. Backend server is running\n2. NVIDIA_API_KEY is configured in .env`);
    } finally {
        analyzeBtn.disabled = false;
        loadingDiv.classList.remove('active');
    }
}

function displayResults(data) {
    // Update status badge
    updateStatusBadge(data.final_status);
    
    // Update iteration count
    iterationCount.textContent = `${data.total_iterations} iteration${data.total_iterations !== 1 ? 's' : ''}`;
    
    // Render timeline
    renderTimeline(data.history);
    
    // Show results
    resultsDiv.classList.add('active');
    
    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function updateStatusBadge(status) {
    statusBadge.className = 'status-badge';
    
    switch(status) {
        case 'safe':
            statusBadge.classList.add('safe');
            statusIcon.textContent = '✓';
            statusText.textContent = 'Code is Secure';
            break;
        case 'healed':
            statusBadge.classList.add('healed');
            statusIcon.textContent = '🛡️';
            statusText.textContent = 'Code Healed Successfully';
            break;
        case 'max_iterations_reached':
            statusBadge.classList.add('warning');
            statusIcon.textContent = '⚠️';
            statusText.textContent = 'Max Iterations Reached';
            break;
    }
}

function renderTimeline(history) {
    timelineDiv.innerHTML = '';
    
    history.forEach((iteration, index) => {
        const card = createIterationCard(iteration, index);
        timelineDiv.appendChild(card);
    });
}

function createIterationCard(iteration, index) {
    const card = document.createElement('div');
    card.className = 'iteration-card';
    
    // Create header
    const header = document.createElement('div');
    header.className = 'iteration-header';
    header.innerHTML = `
        <span class="iteration-title">Iteration ${iteration.iteration + 1}</span>
        <span class="toggle-icon">▼</span>
    `;
    
    // Create body
    const body = document.createElement('div');
    body.className = 'iteration-body';
    
    // Add code snapshot
    body.innerHTML += `
        <div style="margin-bottom: 1.5rem;">
            <div class="code-label">Code Snapshot</div>
            <div class="code-block">
                <code>${escapeHtml(iteration.code_snapshot)}</code>
            </div>
        </div>
    `;
    
    // Add audit report
    if (iteration.audit_report.is_safe) {
        body.innerHTML += `
            <div class="safe-message">
                <div class="safe-icon">✓</div>
                <h3>No Vulnerabilities Found</h3>
                <p>${iteration.audit_report.summary}</p>
            </div>
        `;
    } else {
        body.innerHTML += `
            <div style="margin-bottom: 1.5rem;">
                <h4 style="color: var(--text-secondary); margin-bottom: 1rem;">
                    Detected Vulnerabilities (${iteration.audit_report.vulnerabilities.length})
                </h4>
                ${iteration.audit_report.vulnerabilities.map(vuln => 
                    createVulnerabilityHTML(vuln)
                ).join('')}
            </div>
        `;
    }
    
    // Add fix if applied
    if (iteration.fix_applied) {
        body.innerHTML += `
            <div>
                <div class="code-label">Applied Fix</div>
                <div class="code-block">
                    <code>${escapeHtml(iteration.fix_applied)}</code>
                </div>
            </div>
        `;
    }
    
    // Toggle functionality
    header.addEventListener('click', () => {
        card.classList.toggle('collapsed');
    });
    
    card.appendChild(header);
    card.appendChild(body);
    
    return card;
}

function createVulnerabilityHTML(vuln) {
    return `
        <div class="vulnerability ${vuln.severity}">
            <div class="vuln-header">
                <span class="severity-badge ${vuln.severity}">${vuln.severity}</span>
                <span class="cwe-tag">${vuln.cwe_id}</span>
            </div>
            <div class="vuln-description">${vuln.description}</div>
            ${vuln.line_number ? `<div style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 0.5rem;">Line ${vuln.line_number}</div>` : ''}
            <div class="code-label">Suggested Fix</div>
            <div class="code-block">
                <code>${escapeHtml(vuln.suggested_fix_snippet)}</code>
            </div>
        </div>
    `;
}

function clearResults() {
    codeInput.value = '';
    resultsDiv.classList.remove('active');
    codeInput.focus();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Keyboard shortcuts info
console.log('%c🔐 Self-Healing Code Auditor', 'color: #8b5cf6; font-size: 16px; font-weight: bold;');
console.log('%cKeyboard Shortcuts:', 'color: #7d8590; font-size: 12px;');
console.log('%c  Ctrl+Enter: Analyze code', 'color: #e6edf3; font-size: 12px;');
console.log('%c\nPowered by NVIDIA NIM APIs', 'color: #76b900; font-size: 12px;');
