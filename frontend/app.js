const API_BASE = 'http://127.0.0.1:8000';

// Load data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadData();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('refresh-btn').addEventListener('click', loadData);
    document.getElementById('reconcile-btn').addEventListener('click', runReconciliation);
    document.getElementById('ask-copilot-btn').addEventListener('click', askCopilot);
}

async function loadData() {
    await loadTrades();
    await loadIssues();
    updateStats();
}

async function loadTrades() {
    try {
        const response = await fetch(`${API_BASE}/trades/`);
        const trades = await response.json();
        
        const tbody = document.getElementById('trades-body');
        tbody.innerHTML = '';
        
        trades.forEach(trade => {
            const row = `
                <tr>
                    <td>${trade.trade_id}</td>
                    <td>${trade.trader}</td>
                    <td>${trade.instrument}</td>
                    <td>${trade.quantity}</td>
                    <td>$${trade.price.toFixed(2)}</td>
                    <td><span class="badge badge-${trade.side.toLowerCase()}">${trade.side}</span></td>
                    <td><span class="badge badge-${trade.status.toLowerCase()}">${trade.status}</span></td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
    } catch (error) {
        console.error('Error loading trades:', error);
    }
}

async function loadIssues() {
    try {
        const response = await fetch(`${API_BASE}/issues/`);
        const issues = await response.json();
        
        const tbody = document.getElementById('issues-body');
        tbody.innerHTML = '';
        
        if (issues.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No issues detected ✅</td></tr>';
            return;
        }
        
        issues.forEach(issue => {
            const row = `
                <tr>
                    <td>${issue.id}</td>
                    <td>${issue.issue_type}</td>
                    <td>${issue.description}</td>
                    <td><span class="badge badge-${issue.severity.toLowerCase()}">${issue.severity}</span></td>
                    <td>${issue.trade_id || 'N/A'}</td>
                    <td>
                        <button class="btn btn-primary explain-btn" onclick="explainIssue(${issue.id})">
                            Explain
                        </button>
                    </td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
    } catch (error) {
        console.error('Error loading issues:', error);
    }
}

async function updateStats() {
    try {
        const tradesResponse = await fetch(`${API_BASE}/trades/`);
        const trades = await tradesResponse.json();
        
        const issuesResponse = await fetch(`${API_BASE}/issues/`);
        const issues = await issuesResponse.json();
        
        document.getElementById('total-trades').textContent = trades.length;
        document.getElementById('pending-trades').textContent = 
            trades.filter(t => t.status === 'pending').length;
        document.getElementById('total-issues').textContent = issues.length;
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

async function runReconciliation() {
    const btn = document.getElementById('reconcile-btn');
    btn.classList.add('loading');
    btn.textContent = '⏳ Running...';
    
    try {
        const response = await fetch(`${API_BASE}/reconcile/`, {
            method: 'POST'
        });
        const result = await response.json();
        
        alert(`Reconciliation complete!\n\nIssues found: ${result.total}\n- Trade/Ledger mismatches: ${result.issues.length}\n- Anomalies: ${result.anomalies.length}`);
        
        await loadData();
    } catch (error) {
        console.error('Error running reconciliation:', error);
        alert('Error running reconciliation');
    } finally {
        btn.classList.remove('loading');
        btn.textContent = '🔍 Run Reconciliation';
    }
}

async function explainIssue(issueId) {
    const responseDiv = document.getElementById('copilot-response');
    responseDiv.textContent = 'Loading explanation...';
    
    try {
        const response = await fetch(`${API_BASE}/copilot/explain/${issueId}`, {
            method: 'POST'
        });
        const data = await response.json();
        responseDiv.textContent = data.explanation;
    } catch (error) {
        console.error('Error explaining issue:', error);
        responseDiv.textContent = 'Error getting explanation';
    }
}

async function askCopilot() {
    const query = document.getElementById('copilot-query').value;
    const responseDiv = document.getElementById('copilot-response');
    
    if (!query.trim()) {
        alert('Please enter a question');
        return;
    }
    
    responseDiv.textContent = 'Thinking...';
    
    try {
        const response = await fetch(`${API_BASE}/copilot/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });
        const data = await response.json();
        responseDiv.textContent = data.answer;
    } catch (error) {
        console.error('Error asking copilot:', error);
        responseDiv.textContent = 'Error getting response';
    }
}