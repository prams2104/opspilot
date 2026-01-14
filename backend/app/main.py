from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import engine, get_db, Base
from .models import Trade, LedgerEntry, ReconciliationIssue
from .reconciliation import ReconciliationEngine
from .ai_copilot import AICopilot
from pydantic import BaseModel
from typing import List
from datetime import datetime

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="OpsPilot API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TradeCreate(BaseModel):
    trade_id: str
    trader: str
    instrument: str
    quantity: float
    price: float
    side: str

class CopilotQuery(BaseModel):
    query: str

@app.get("/")
def root():
    return {"message": "OpsPilot API - Operations Reconciliation Copilot"}

@app.post("/trades/")
def create_trade(trade: TradeCreate, db: Session = Depends(get_db)):
    db_trade = Trade(**trade.dict())
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

@app.get("/trades/")
def get_trades(db: Session = Depends(get_db)):
    return db.query(Trade).all()

@app.get("/issues/")
def get_issues(db: Session = Depends(get_db)):
    return db.query(ReconciliationIssue).filter(
        ReconciliationIssue.resolved == False
    ).all()

@app.post("/reconcile/")
def run_reconciliation(db: Session = Depends(get_db)):
    engine = ReconciliationEngine(db)
    issues = engine.check_trade_ledger_match()
    anomalies = engine.detect_anomalies()
    return {
        "issues": issues,
        "anomalies": anomalies,
        "total": len(issues) + len(anomalies)
    }

@app.post("/copilot/explain/{issue_id}")
def explain_issue(issue_id: int, db: Session = Depends(get_db)):
    copilot = AICopilot(db)
    explanation = copilot.explain_issue(issue_id)
    return {"explanation": explanation}

@app.post("/copilot/query")
def copilot_query(query: CopilotQuery, db: Session = Depends(get_db)):
    copilot = AICopilot(db)
    answer = copilot.answer_query(query.query)
    return {"answer": answer}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}