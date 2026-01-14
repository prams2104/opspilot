from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime
from .database import Base

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String, unique=True, index=True)
    trader = Column(String)
    instrument = Column(String)
    quantity = Column(Float)
    price = Column(Float)
    side = Column(String)  # BUY/SELL
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")

class LedgerEntry(Base):
    __tablename__ = "ledger"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String, index=True)
    amount = Column(Float)
    currency = Column(String)
    entry_type = Column(String)  # DEBIT/CREDIT
    timestamp = Column(DateTime, default=datetime.utcnow)
    reconciled = Column(Boolean, default=False)

class ReconciliationIssue(Base):
    __tablename__ = "issues"
    
    id = Column(Integer, primary_key=True, index=True)
    issue_type = Column(String)
    description = Column(String)
    severity = Column(String)  # LOW/MEDIUM/HIGH/CRITICAL
    trade_id = Column(String, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)
    ai_explanation = Column(String, nullable=True)