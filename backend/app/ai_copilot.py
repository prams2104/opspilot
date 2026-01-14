from .config import get_settings
from sqlalchemy.orm import Session
from .models import ReconciliationIssue, Trade
from typing import List, Dict

settings = get_settings()

class AICopilot:
    def __init__(self, db: Session):
        self.db = db
    
    def explain_issue(self, issue_id: int) -> str:
        """Explain a reconciliation issue (placeholder for now)"""
        issue = self.db.query(ReconciliationIssue).filter(
            ReconciliationIssue.id == issue_id
        ).first()
        
        if not issue:
            return "Issue not found"
        
        # Get related trade info
        trade = None
        if issue.trade_id:
            trade = self.db.query(Trade).filter(
                Trade.trade_id == issue.trade_id
            ).first()
        
        # Simple rule-based explanation for now
        explanation = f"Issue: {issue.issue_type}\n"
        explanation += f"Severity: {issue.severity}\n"
        explanation += f"Description: {issue.description}\n"
        
        if trade:
            explanation += f"\nRelated Trade:\n"
            explanation += f"- Trader: {trade.trader}\n"
            explanation += f"- Instrument: {trade.instrument}\n"
            explanation += f"- Amount: {trade.quantity} @ {trade.price}\n"
        
        explanation += "\n[AI explanation will be added when API key is configured]"
        
        return explanation
    
    def answer_query(self, query: str) -> str:
        """Answer natural language questions (placeholder for now)"""
        # Get current issues
        issues = self.db.query(ReconciliationIssue).filter(
            ReconciliationIssue.resolved == False
        ).all()
        
        total_trades = self.db.query(Trade).count()
        pending_trades = self.db.query(Trade).filter(Trade.status == "pending").count()
        
        response = f"System Status:\n"
        response += f"- Total Trades: {total_trades}\n"
        response += f"- Pending Trades: {pending_trades}\n"
        response += f"- Open Issues: {len(issues)}\n\n"
        
        if issues:
            response += "Recent Issues:\n"
            for issue in issues[:5]:
                response += f"- {issue.issue_type}: {issue.description}\n"
        
        response += "\n[Full AI responses will be available when API key is configured]"
        
        return response