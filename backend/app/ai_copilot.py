from .config import get_settings
from sqlalchemy.orm import Session
from .models import ReconciliationIssue, Trade, LedgerEntry
from typing import List, Dict
import anthropic
import os

settings = get_settings()

class AICopilot:
    def __init__(self, db: Session):
        self.db = db
        self.client = None
        
        # Only initialize Anthropic client if API key is set and not dummy
        api_key = settings.anthropic_api_key
        if api_key and api_key != "dummy_key":
            self.client = anthropic.Anthropic(api_key=api_key)
    
    def _get_system_context(self) -> str:
        """Build context about current system state"""
        total_trades = self.db.query(Trade).count()
        pending_trades = self.db.query(Trade).filter(Trade.status == "pending").count()
        total_ledger = self.db.query(LedgerEntry).count()
        open_issues = self.db.query(ReconciliationIssue).filter(
            ReconciliationIssue.resolved == False
        ).count()
        
        context = f"""You are an AI assistant for OpsPilot, an operations reconciliation system.

Current System State:
- Total Trades: {total_trades}
- Pending Trades: {pending_trades}
- Ledger Entries: {total_ledger}
- Open Reconciliation Issues: {open_issues}

Your role is to help operations teams understand reconciliation issues, explain discrepancies, 
and provide actionable insights about the system's data quality.
"""
        return context
    
    def _get_issue_details(self, issue_id: int) -> Dict:
        """Get detailed information about an issue and related data"""
        issue = self.db.query(ReconciliationIssue).filter(
            ReconciliationIssue.id == issue_id
        ).first()
        
        if not issue:
            return None
        
        result = {
            "issue": {
                "id": issue.id,
                "type": issue.issue_type,
                "description": issue.description,
                "severity": issue.severity,
                "trade_id": issue.trade_id,
                "detected_at": str(issue.detected_at),
            },
            "trade": None,
            "ledger_entries": []
        }
        
        # Get related trade
        if issue.trade_id:
            trade = self.db.query(Trade).filter(
                Trade.trade_id == issue.trade_id
            ).first()
            
            if trade:
                result["trade"] = {
                    "trade_id": trade.trade_id,
                    "trader": trade.trader,
                    "instrument": trade.instrument,
                    "quantity": trade.quantity,
                    "price": trade.price,
                    "side": trade.side,
                    "timestamp": str(trade.timestamp),
                    "expected_amount": trade.quantity * trade.price
                }
                
                # Get related ledger entries
                ledger_entries = self.db.query(LedgerEntry).filter(
                    LedgerEntry.trade_id == issue.trade_id
                ).all()
                
                result["ledger_entries"] = [
                    {
                        "amount": entry.amount,
                        "currency": entry.currency,
                        "entry_type": entry.entry_type,
                        "timestamp": str(entry.timestamp)
                    }
                    for entry in ledger_entries
                ]
        
        return result
    
    def explain_issue(self, issue_id: int) -> str:
        """Explain a reconciliation issue using AI"""
        details = self._get_issue_details(issue_id)
        
        if not details:
            return "Issue not found"
        
        # If no API client, return basic explanation
        if not self.client:
            return self._generate_basic_explanation(details)
        
        # Generate AI-powered explanation
        try:
            prompt = self._build_issue_explanation_prompt(details)
            
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            explanation = message.content[0].text
            
            # Store the AI explanation in the database
            issue = self.db.query(ReconciliationIssue).filter(
                ReconciliationIssue.id == issue_id
            ).first()
            issue.ai_explanation = explanation
            self.db.commit()
            
            return explanation
            
        except Exception as e:
            return f"Error generating AI explanation: {str(e)}\n\n{self._generate_basic_explanation(details)}"
    
    def _build_issue_explanation_prompt(self, details: Dict) -> str:
        """Build a detailed prompt for issue explanation"""
        issue = details["issue"]
        trade = details["trade"]
        ledger = details["ledger_entries"]
        
        prompt = f"""I need you to explain a reconciliation issue in clear, actionable language for an operations team.

Issue Details:
- Type: {issue['type']}
- Severity: {issue['severity']}
- Description: {issue['description']}
- Detected: {issue['detected_at']}
"""
        
        if trade:
            prompt += f"""
Trade Information:
- Trade ID: {trade['trade_id']}
- Trader: {trade['trader']}
- Instrument: {trade['instrument']}
- Quantity: {trade['quantity']}
- Price: ${trade['price']}
- Side: {trade['side']}
- Expected Amount: ${trade['expected_amount']}
- Trade Time: {trade['timestamp']}
"""
        
        if ledger:
            prompt += f"\nLedger Entries Found: {len(ledger)}\n"
            for entry in ledger:
                prompt += f"- {entry['entry_type']}: {entry['currency']} {entry['amount']} at {entry['timestamp']}\n"
        else:
            prompt += "\nLedger Entries Found: None\n"
        
        prompt += """
Please provide:
1. A clear explanation of what went wrong
2. The potential business impact
3. Recommended next steps to resolve this issue
4. Any patterns or root causes to investigate

Keep the explanation concise but thorough, suitable for both technical and non-technical stakeholders.
"""
        
        return prompt
    
    def _generate_basic_explanation(self, details: Dict) -> str:
        """Generate a basic rule-based explanation when AI is not available"""
        issue = details["issue"]
        trade = details["trade"]
        ledger = details["ledger_entries"]
        
        explanation = f"Issue: {issue['type']}\n"
        explanation += f"Severity: {issue['severity']}\n"
        explanation += f"Description: {issue['description']}\n\n"
        
        if trade:
            explanation += f"Related Trade:\n"
            explanation += f"- Trader: {trade['trader']}\n"
            explanation += f"- Instrument: {trade['instrument']}\n"
            explanation += f"- Amount: {trade['quantity']} @ ${trade['price']} = ${trade['expected_amount']}\n\n"
        
        if issue['type'] == 'MISSING_LEDGER_ENTRY':
            explanation += "Problem: This trade has no corresponding ledger entry.\n"
            explanation += "Impact: The trade is not reflected in the books, creating an accounting gap.\n"
            explanation += "Action: Verify if the ledger entry was created but with a different ID, or create the missing entry.\n"
        
        elif issue['type'] == 'AMOUNT_MISMATCH':
            if trade and ledger:
                ledger_total = sum(e['amount'] for e in ledger)
                explanation += f"Problem: Expected ${trade['expected_amount']}, but ledger shows ${abs(ledger_total)}.\n"
                explanation += f"Difference: ${abs(trade['expected_amount'] - abs(ledger_total))}\n"
            explanation += "Impact: Books don't match trade records, indicating a calculation or entry error.\n"
            explanation += "Action: Review the ledger entry calculation and correct the amount.\n"
        
        elif issue['type'] == 'ANOMALOUS_QUANTITY':
            explanation += "Problem: This trade quantity is significantly higher than average.\n"
            explanation += "Impact: Could indicate a fat-finger error, unauthorized trading, or legitimate large trade.\n"
            explanation += "Action: Verify the trade with the trader and their supervisor.\n"
        
        explanation += "\n[Configure ANTHROPIC_API_KEY in .env for AI-powered explanations]"
        
        return explanation
    
    def answer_query(self, query: str) -> str:
        """Answer natural language questions about the system"""
        # Get current system state
        issues = self.db.query(ReconciliationIssue).filter(
            ReconciliationIssue.resolved == False
        ).all()
        
        trades = self.db.query(Trade).all()
        total_trades = len(trades)
        pending_trades = len([t for t in trades if t.status == "pending"])
        
        # If no API client, return basic response
        if not self.client:
            return self._generate_basic_query_response(query, issues, total_trades, pending_trades)
        
        # Generate AI-powered response
        try:
            system_context = self._get_system_context()
            
            # Build detailed context about issues
            issues_context = ""
            if issues:
                issues_context = "\n\nCurrent Open Issues:\n"
                for issue in issues:
                    issues_context += f"- {issue.issue_type} (Severity: {issue.severity}): {issue.description}\n"
                    if issue.trade_id:
                        issues_context += f"  Trade ID: {issue.trade_id}\n"
            
            # Build context about trades
            trades_context = "\n\nRecent Trades:\n"
            for trade in trades[-5:]:  # Last 5 trades
                trades_context += f"- {trade.trade_id}: {trade.trader} - {trade.instrument} ({trade.side}) - {trade.quantity}@${trade.price}\n"
            
            full_context = system_context + issues_context + trades_context
            
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                system=full_context,
                messages=[
                    {"role": "user", "content": query}
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            return f"Error generating AI response: {str(e)}\n\n{self._generate_basic_query_response(query, issues, total_trades, pending_trades)}"
    
    def _generate_basic_query_response(self, query: str, issues: List, total_trades: int, pending_trades: int) -> str:
        """Generate a basic response when AI is not available"""
        response = f"System Status:\n"
        response += f"- Total Trades: {total_trades}\n"
        response += f"- Pending Trades: {pending_trades}\n"
        response += f"- Open Issues: {len(issues)}\n\n"
        
        if issues:
            response += "Recent Issues:\n"
            for issue in issues[:5]:
                response += f"- {issue.issue_type}: {issue.description}\n"
        else:
            response += "No open issues - system is healthy! ✅\n"
        
        response += "\n[Configure ANTHROPIC_API_KEY in .env for AI-powered query responses]"
        
        return response