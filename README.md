# OpsPilot

An AI-powered operations reconciliation system that automates data validation, detects anomalies, and provides intelligent explanations for operational discrepancies.

## Demo

![OpsPilot Dashboard](docs/dashboard.png)

*Real-time reconciliation dashboard showing trades, detected issues, and AI-powered analysis*

## Overview

OpsPilot addresses a critical enterprise challenge: reconciling operational data across systems. When trades are executed, ledger entries must match. When invoices are generated, payments must align. This system automates the detection and diagnosis of these mismatches.

Built with modern Python tooling and designed to mirror production systems used in financial services, supply chain operations, and enterprise analytics.

## Features

- **Automated Reconciliation Engine**: Validates trade data against ledger entries, detecting mismatches and missing records
- **Anomaly Detection**: Statistical analysis to flag unusual transactions (e.g., quantities 5x above average)
- **AI-Powered Explanations**: Natural language explanations of detected issues using Claude API with graceful fallback
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

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/opspilot.git
cd opspilot
```

2. **Create and activate virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r backend/app/requirements.txt
```

4. **Configure environment variables:**

Create a `.env` file in the root directory:
```env
DATABASE_URL=sqlite:///./opspilot.db
ANTHROPIC_API_KEY=dummy_key  # See AI Features section below
ENVIRONMENT=development
```

5. **Load sample data:**
```bash
cd backend/app
python load_data_standalone.py
cd ../..
```

6. **Start the API server:**
```bash
python -m uvicorn backend.app.main:app --reload
```

7. **Open the frontend:**

Open `frontend/index.html` in your web browser, or serve it locally:
```bash
python -m http.server 8080
# Then visit: http://localhost:8080/frontend/
```

The API will be available at `http://127.0.0.1:8000` with documentation at `http://127.0.0.1:8000/docs`.

## AI Features

The AI Copilot provides intelligent explanations and natural language query capabilities. **The system works perfectly with or without AI enabled.**

### Using Without AI (Default Setup)

- System provides rule-based explanations for all issues
- All core reconciliation features work normally
- Perfect for development, testing, and demonstrations
- No API costs or external dependencies

### Enabling AI (Optional)

To enable Claude API integration for enhanced explanations:

1. Sign up at https://console.anthropic.com/
2. Purchase credits ($5 minimum, lasts months for this project)
3. Update `.env` file:
   ```env
   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
   ```
4. Restart the server

**Note**: The fallback explanations are production-ready and demonstrate the same system architecture. AI integration showcases external API handling and graceful degradation patterns.

### AI Capabilities

When enabled, the AI Copilot provides:

**Issue Explanations:**
- Detailed analysis of what went wrong
- Business impact assessment
- Actionable resolution steps
- Root cause investigation guidance

**Natural Language Queries:**
- "What issues need attention?"
- "Summarize the system status"
- "What's wrong with trade TRD003?"
- "Which trader has the most issues?"

## Usage

### Adding Sample Data

The `load_data_standalone.py` script loads sample trades and ledger entries. Alternatively, use the API:

```python
import requests

trade = {
    "trade_id": "TRD001",
    "trader": "Alice",
    "instrument": "AAPL",
    "quantity": 100,
    "price": 150.50,
    "side": "BUY"
}

requests.post("http://127.0.0.1:8000/trades/", json=trade)
```

### Running Reconciliation

**Via Web Interface:**
- Click "Run Reconciliation" button in the dashboard

**Via API:**
```bash
curl -X POST http://127.0.0.1:8000/reconcile/
```

**What it does:**
- Checks all pending trades for matching ledger entries
- Validates amounts match (quantity × price)
- Detects statistical anomalies
- Creates reconciliation issues for problems found

### Querying the AI Copilot

**Via Web Interface:**
- Type your question in the AI Copilot text box
- Click "Ask AI"

**Via API:**
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

Full API documentation available at `http://127.0.0.1:8000/docs` when server is running.

## Project Structure

```
opspilot/
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── main.py                    # FastAPI application & endpoints
│       ├── database.py                # Database connection setup
│       ├── models.py                  # SQLAlchemy ORM models
│       ├── reconciliation.py          # Business logic & validation
│       ├── ai_copilot.py              # AI integration with Claude API
│       ├── config.py                  # Configuration management
│       ├── requirements.txt           # Python dependencies
│       └── load_data_standalone.py    # Sample data loader
├── frontend/
│   ├── index.html                     # Web interface
│   ├── styles.css                     # Styling
│   └── app.js                         # Frontend logic
├── data/
│   ├── sample_trades.csv              # Sample trade data
│   └── sample_ledger.csv              # Sample ledger data
├── docs/
│   ├── ARCHITECTURE.md                # Detailed architecture docs
│   └── images/
│       └── dashboard.png              # Dashboard screenshot
├── .env                               # Environment variables (create this)
├── .gitignore                         # Git ignore rules
├── LICENSE                            # MIT License
└── README.md                          # This file
```

## Real-World Applications

This system architecture is directly applicable to:

- **Financial Services**: Trade reconciliation, payment matching, regulatory reporting
- **Supply Chain**: Invoice verification, shipment tracking validation
- **Healthcare**: Claims processing, prescription reconciliation
- **E-commerce**: Order fulfillment validation, inventory reconciliation
- **Enterprise Operations**: Multi-system data validation, audit trails

## Development

### Running Tests

```bash
pytest backend/app/tests/
```

*(Note: Test suite coming soon)*

### Code Style

This project follows PEP 8 guidelines for Python code.

## Production Considerations

**Current Implementation (Development):**
- SQLite database (file-based)
- No authentication
- CORS enabled for all origins
- Single-server deployment

**Production Recommendations:**
- Migrate to PostgreSQL for scalability
- Implement JWT-based authentication
- Add rate limiting and request throttling
- Enable HTTPS/TLS
- Use secrets manager for API keys
- Implement comprehensive logging
- Add monitoring and alerting
- Deploy with Docker/Kubernetes
- Use gunicorn with multiple workers
- Set up CI/CD pipeline

## Future Enhancements

- PostgreSQL support for production deployments
- Real-time streaming reconciliation with Kafka
- Advanced ML-based anomaly detection
- Multi-tenant architecture
- Audit logging and compliance reporting
- Integration with external data sources (APIs, FTP, message queues)
- Automated issue resolution workflows
- Role-based access control (RBAC)
- Docker containerization
- Comprehensive test suite

## Cost Analysis

**Development/Demo:**
- Free with rule-based explanations
- Optional: $5 Anthropic credits (~2,500 AI explanations)

**Production Estimate (1000 reconciliations/day):**
- Claude API: ~$3-5/month
- Hosting (Railway/Render/AWS): $10-50/month
- Database: $10-20/month (managed PostgreSQL)
- **Total: ~$25-75/month**

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

**Pramesh Singhavi**

- Email: prameshsinghavi02@gmail.com
- LinkedIn: [linkedin.com/in/prameshsinghavi](https://www.linkedin.com/in/pramesh-singhavi-81bab6286/)
- Website: [theunchartedangles.com](https://www.theunchartedangles.com/)
- GitHub: [@prams2104](https://github.com/prams2104)

## Acknowledgments

Built with FastAPI, SQLAlchemy, and Anthropic Claude API. Inspired by real-world reconciliation systems used in financial services and enterprise operations.

---

**⭐ If you find this project useful, please consider starring it on GitHub!**
