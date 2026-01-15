# OpsPilot Architecture

## System Design

OpsPilot follows a three-tier architecture pattern commonly used in enterprise applications.

### Layers

1. Presentation Layer (Frontend)
   - Single-page HTML application
   - JavaScript for API interaction
   - No framework dependencies for simplicity

2. Application Layer (API)
   - FastAPI REST endpoints
   - Request validation with Pydantic
   - CORS enabled for local development

3. Data Layer
   - SQLAlchemy ORM
   - SQLite for development
   - Designed for easy PostgreSQL migration

### Data Flow
```
User Action → API Request → Business Logic → Database Query → Response
                                ↓
                          AI Processing (optional)
```

## Core Components

### Reconciliation Engine

The reconciliation engine implements two primary validation strategies:

1. Trade-Ledger Matching
   - For each pending trade, queries for matching ledger entries
   - Validates that entry exists
   - Validates that amounts match (trade quantity * price)
   - Creates ReconciliationIssue if discrepancies found

2. Statistical Anomaly Detection
   - Calculates average trade quantity
   - Flags trades exceeding 5x average as anomalous
   - Extensible for additional statistical checks

### Database Schema

**Trades Table**
- Primary key: id (auto-increment)
- Unique key: trade_id (business key)
- Foreign key relationships: None (intentionally denormalized)

**Ledger Entries Table**
- Primary key: id (auto-increment)
- Index: trade_id (for reconciliation queries)
- No foreign key constraint (supports missing entries)

**Reconciliation Issues Table**
- Primary key: id (auto-increment)
- Nullable: trade_id (some issues may not relate to specific trade)
- Tracks: issue type, severity, resolution status

### API Design Principles

1. RESTful endpoints following standard conventions
2. Consistent error handling with HTTP status codes
3. JSON request/response format
4. Idempotent POST operations where applicable

### AI Integration

The AI Copilot uses Claude API for:
- Natural language explanations of technical issues
- System state summarization
- Query answering based on current data

Implementation uses context injection: current system state is provided to Claude with each request to ensure accurate, data-driven responses.

## Technology Choices

### Why FastAPI?
- Automatic API documentation (OpenAPI/Swagger)
- Type hints for request validation
- Async support for future scalability
- Popular in production systems

### Why SQLAlchemy?
- Database agnostic (easy PostgreSQL migration)
- Pythonic query interface
- Connection pooling
- Industry standard ORM

### Why SQLite for Development?
- Zero configuration
- File-based (easy to reset/version)
- Sufficient for demo purposes
- Quick local development

## Deployment Considerations

### Production Recommendations

1. Database: Migrate to PostgreSQL
2. API Server: Use gunicorn with multiple workers
3. Frontend: Serve via nginx
4. Security: Add authentication/authorization
5. Monitoring: Add logging, metrics, alerting

### Scalability Points

- Reconciliation engine can be moved to background tasks (Celery)
- Database can be sharded by date or instrument
- API can be horizontally scaled behind load balancer
- AI calls can be cached or batched

## Security Considerations

Current implementation is development-focused. Production deployment requires:

- API authentication (JWT tokens)
- Rate limiting
- Input sanitization (already handled by Pydantic)
- HTTPS/TLS
- Database credential management (secrets manager)
- SQL injection protection (ORM provides this)

## Extension Points

### Adding New Validation Rules

Add methods to ReconciliationEngine class:
```python
def check_custom_rule(self) -> List[Dict]:
    # Custom validation logic
    # Create ReconciliationIssue if fails
    pass
```

### Adding New Data Sources

Extend models.py with new tables, add corresponding API endpoints.

### Integrating External Systems

Add connector modules in new directory (e.g., backend/app/connectors/) for APIs, message queues, or file systems.