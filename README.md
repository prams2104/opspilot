# OpsPilot

An AI-powered operations reconciliation system that automates data validation, detects anomalies, and provides intelligent explanations for operational discrepancies.

## Overview

OpsPilot addresses a common enterprise problem: reconciling operational data across systems. When trades are executed, ledger entries must match. When invoices are generated, payments must align. This system automates the detection and diagnosis of these mismatches.

Built with modern Python tooling and designed to mirror production systems used in financial services, supply chain operations, and enterprise analytics.

## Features

- **Automated Reconciliation Engine**: Validates trade data against ledger entries, detecting mismatches and missing records
- **Anomaly Detection**: Statistical analysis to flag unusual transactions (e.g., quantities 5x above average)
- **AI-Powered Explanations**: Natural language explanations of detected issues using Claude API
- **REST API**: Full CRUD operations for trades, ledger entries, and reconciliation issues
- **Web Dashboard**: Real-time visualization of system status, trades, and issues
- **Extensible Architecture**: Modular design supports adding new validation rules and data sources

## Architecture
```
Frontend (HTML/JS) → REST API (FastAPI) → Business Logic (Python) → Database (SQLite)
                                          ↓
                                    AI Copilot (Anthropic Claude)
```

### Core Components

- **API Layer** (`main.py`): FastAPI endpoints for data access and operations
- **Database Models** (`models.py`): SQLAlchemy ORM definitions for trades, ledger entries, and issues
- **Reconciliation Engine** (`reconciliation.py`): Business logic for validation and anomaly detection
- **AI Copilot** (`ai_copilot.py`): Natural language interface for issue explanation and system queries
- **Frontend**: Single-page application for data visualization and interaction

## Technology Stack

**Backend:**
- Python 3.12
- FastAPI (REST API framework)
- SQLAlchemy (ORM)
- SQLite (database)
- Anthropic Claude API (AI capabilities)

**Frontend:**
- Vanilla JavaScript
- HTML5/CSS3

**Development:**
- uvicorn (ASGI server)
- Virtual environment (venv)

## Setup Instructions

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd opspilot
```

2. Create and activate virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r backend/app/requirements.txt
```

4. Configure environment variables:
```bash
# Create .env file in root directory
DATABASE_URL=sqlite:///./opspilot.db
ANTHROPIC_API_KEY=your_api_key_here  # Optional: leave as dummy_key for testing
ENVIRONMENT=development
```

5. Start the API server:
```bash
python -m uvicorn backend.app.main:app --reload
```

6. Open the frontend:
```bash
open frontend/index.html  # Or double-click the file
```

The API will be available at `http://127.0.0.1:8000` and documentation at `http://127.0.0.1:8000/docs`.

## Usage

### Adding Sample Data

Use the API docs interface at `http://127.0.0.1:8000/docs` or run this Python script:
```python
import requests

trades = [
    {
        "trade_id": "TRD001",
        "trader": "Alice",
        "instrument": "AAPL",
        "quantity": 100,
        "price": 150.50,
        "side": "BUY"
    }
]

for trade in trades:
    requests.post("http://127.0.0.1:8000/trades/", json=trade)
```

### Running Reconciliation

Click "Run Reconciliation" in the web dashboard, or call the API directly:
```bash
curl -X POST http://127.0.0.1:8000/reconcile/
```

### Querying the AI Copilot

Use the web interface or API:
```bash
curl -X POST http://127.0.0.1:8000/copilot/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What issues need attention?"}'
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API health check |
| GET | `/trades/` | List all trades |
| POST | `/trades/` | Create new trade |
| GET | `/issues/` | List open reconciliation issues |
| POST | `/reconcile/` | Run reconciliation checks |
| POST | `/copilot/explain/{issue_id}` | Get AI explanation for specific issue |
| POST | `/copilot/query` | Ask natural language questions |
| GET | `/health` | System health status |

## Project Structure
```
opspilot/
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI application
│       ├── database.py          # Database connection
│       ├── models.py            # SQLAlchemy models
│       ├── reconciliation.py   # Business logic
│       ├── ai_copilot.py       # AI integration
│       ├── config.py           # Configuration
│       └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html              # Web interface
│   ├── styles.css              # Styling
│   └── app.js                  # Frontend logic
├── data/
│   ├── sample_trades.csv       # Sample data
│   └── sample_ledger.csv       # Sample data
├── .env                         # Environment variables
└── README.md
```

## Development

### Running Tests
```bash
pytest backend/app/tests/
```

### Code Style

This project follows PEP 8 guidelines for Python code.

## Real-World Applications

This system architecture is applicable to:

- **Financial Services**: Trade reconciliation, payment matching, regulatory reporting
- **Supply Chain**: Invoice verification, shipment tracking validation
- **Healthcare**: Claims processing, prescription reconciliation
- **E-commerce**: Order fulfillment validation, inventory reconciliation

## Future Enhancements

- PostgreSQL support for production deployments
- Real-time streaming reconciliation with Kafka
- Advanced ML-based anomaly detection
- Multi-tenant architecture
- Audit logging and compliance reporting
- Integration with external data sources (APIs, FTP, message queues)

## License

MIT

## Contact

Pramesh Singhavi