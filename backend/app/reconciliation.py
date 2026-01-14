from sqlalchemy.orm import Session
from .models import Trade, LedgerEntry, ReconciliationIssue
from datetime import datetime
from typing import List, Dict

class ReconciliationEngine:
    def __init__(self, db: Session):
        self.db = db
    
    def check_trade_ledger_match(self) -> List[Dict]:
        """Check if trades match ledger entries"""
        issues = []
        trades = self.db.query(Trade).filter(Trade.status == "pending").all()
        
        for trade in trades:
            ledger_entries = self.db.query(LedgerEntry).filter(
                LedgerEntry.trade_id == trade.trade_id
            ).all()
            
            if not ledger_entries:
                issue = ReconciliationIssue(
                    issue_type="MISSING_LEDGER_ENTRY",
                    description=f"Trade {trade.trade_id} has no corresponding ledger entry",
                    severity="HIGH",
                    trade_id=trade.trade_id
                )
                self.db.add(issue)
                issues.append({
                    "type": "MISSING_LEDGER_ENTRY",
                    "trade_id": trade.trade_id,
                    "severity": "HIGH"
                })
            else:
                # Check amount matching
                expected_amount = trade.quantity * trade.price
                total_ledger = sum(entry.amount for entry in ledger_entries)
                
                if abs(expected_amount - abs(total_ledger)) > 0.01:
                    issue = ReconciliationIssue(
                        issue_type="AMOUNT_MISMATCH",
                        description=f"Trade {trade.trade_id}: Expected {expected_amount}, Got {total_ledger}",
                        severity="CRITICAL",
                        trade_id=trade.trade_id
                    )
                    self.db.add(issue)
                    issues.append({
                        "type": "AMOUNT_MISMATCH",
                        "trade_id": trade.trade_id,
                        "expected": expected_amount,
                        "actual": total_ledger,
                        "severity": "CRITICAL"
                    })
        
        self.db.commit()
        return issues
    
    def detect_anomalies(self) -> List[Dict]:
        """Detect statistical anomalies"""
        issues = []
        trades = self.db.query(Trade).all()
        
        if not trades:
            return issues
        
        # Simple anomaly: unusually large trade
        avg_quantity = sum(t.quantity for t in trades) / len(trades)
        
        for trade in trades:
            if trade.quantity > avg_quantity * 5:  # 5x average
                issue = ReconciliationIssue(
                    issue_type="ANOMALOUS_QUANTITY",
                    description=f"Trade {trade.trade_id} has unusually large quantity: {trade.quantity}",
                    severity="MEDIUM",
                    trade_id=trade.trade_id
                )
                self.db.add(issue)
                issues.append({
                    "type": "ANOMALOUS_QUANTITY",
                    "trade_id": trade.trade_id,
                    "quantity": trade.quantity,
                    "severity": "MEDIUM"
                })
        
        self.db.commit()
        return issues