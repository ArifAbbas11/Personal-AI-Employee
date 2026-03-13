"""
Financial Agent

Specialized agent for financial management, accounting automation, and financial analysis.
Integrates with Odoo accounting and ML expense categorization.
"""

import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_agent.base import (
    BaseAgent,
    AgentRole,
    AgentCapability,
    AgentTask,
    AgentCoordinator,
    TaskPriority
)

# Import ML model for expense categorization
from ml_engine.expense_categorizer import ExpenseCategorizer

logger = logging.getLogger(__name__)


class FinancialAgent(BaseAgent):
    """Agent specialized in financial management and accounting."""

    def __init__(
        self,
        vault_path: str = "AI_Employee_Vault",
        coordinator: Optional[AgentCoordinator] = None
    ):
        """
        Initialize Financial Agent.

        Args:
            vault_path: Path to AI_Employee_Vault
            coordinator: Optional agent coordinator
        """
        super().__init__(
            agent_id="financial_agent",
            role=AgentRole.FINANCIAL,
            vault_path=vault_path,
            coordinator=coordinator
        )

        # Initialize ML model for expense categorization
        try:
            self.expense_categorizer = ExpenseCategorizer(vault_path)
            logger.info("Expense categorizer loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load expense categorizer: {e}")
            self.expense_categorizer = None

        # Financial data cache
        self.accounts: Dict[str, Dict[str, Any]] = {}
        self.transactions: List[Dict[str, Any]] = []
        self.budgets: Dict[str, Dict[str, Any]] = {}

    def _initialize_capabilities(self) -> None:
        """Initialize financial agent capabilities."""
        self.capabilities = [
            AgentCapability(
                capability_id="categorize_expense",
                name="Categorize Expense",
                description="Automatically categorize expenses using ML",
                input_schema={
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "amount": {"type": "number"},
                        "vendor": {"type": "string"}
                    },
                    "required": ["description", "amount"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "category": {"type": "string"},
                        "confidence": {"type": "number"}
                    }
                },
                estimated_duration_seconds=5
            ),
            AgentCapability(
                capability_id="record_transaction",
                name="Record Transaction",
                description="Record a financial transaction",
                input_schema={
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["income", "expense"]},
                        "amount": {"type": "number"},
                        "description": {"type": "string"},
                        "category": {"type": "string"},
                        "date": {"type": "string"}
                    },
                    "required": ["type", "amount", "description"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "transaction_id": {"type": "string"},
                        "recorded": {"type": "boolean"}
                    }
                },
                estimated_duration_seconds=10
            ),
            AgentCapability(
                capability_id="generate_financial_report",
                name="Generate Financial Report",
                description="Generate financial reports (P&L, balance sheet, cash flow)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "report_type": {
                            "type": "string",
                            "enum": ["profit_loss", "balance_sheet", "cash_flow", "summary"]
                        },
                        "start_date": {"type": "string"},
                        "end_date": {"type": "string"}
                    },
                    "required": ["report_type"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "report": {"type": "object"}
                    }
                },
                estimated_duration_seconds=30
            ),
            AgentCapability(
                capability_id="analyze_spending",
                name="Analyze Spending",
                description="Analyze spending patterns and identify trends",
                input_schema={
                    "type": "object",
                    "properties": {
                        "period_days": {"type": "integer"},
                        "category": {"type": "string"}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "analysis": {"type": "object"}
                    }
                },
                estimated_duration_seconds=20
            ),
            AgentCapability(
                capability_id="check_budget",
                name="Check Budget",
                description="Check budget status and alert on overruns",
                input_schema={
                    "type": "object",
                    "properties": {
                        "category": {"type": "string"},
                        "period": {"type": "string"}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "object"}
                    }
                },
                estimated_duration_seconds=10
            ),
            AgentCapability(
                capability_id="reconcile_accounts",
                name="Reconcile Accounts",
                description="Reconcile bank accounts with recorded transactions",
                input_schema={
                    "type": "object",
                    "properties": {
                        "account_id": {"type": "string"},
                        "statement_date": {"type": "string"}
                    },
                    "required": ["account_id"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "reconciliation": {"type": "object"}
                    }
                },
                estimated_duration_seconds=60,
                requires_human_approval=True
            )
        ]

    def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Process a financial task.

        Args:
            task: Task to process

        Returns:
            Task result dictionary
        """
        task_type = task.task_type
        metadata = task.metadata

        if task_type == "categorize_expense":
            return self._categorize_expense(metadata)
        elif task_type == "record_transaction":
            return self._record_transaction(metadata)
        elif task_type == "generate_financial_report":
            return self._generate_financial_report(metadata)
        elif task_type == "analyze_spending":
            return self._analyze_spending(metadata)
        elif task_type == "check_budget":
            return self._check_budget(metadata)
        elif task_type == "reconcile_accounts":
            return self._reconcile_accounts(metadata)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    def _categorize_expense(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Categorize an expense using ML."""
        description = data.get('description', '')
        amount = data.get('amount', 0)
        vendor = data.get('vendor', '')

        if self.expense_categorizer and self.expense_categorizer.is_trained:
            # Use ML model
            result = self.expense_categorizer.predict({
                'description': description,
                'amount': amount,
                'vendor': vendor
            })
            category = result['category']
            confidence = result['confidence']
        else:
            # Fallback to heuristic categorization
            category = self._heuristic_categorize(description, amount)
            confidence = 0.5

        return {
            'success': True,
            'category': category,
            'confidence': confidence,
            'description': description,
            'amount': amount
        }

    def _heuristic_categorize(self, description: str, amount: float) -> str:
        """Fallback heuristic categorization."""
        desc_lower = description.lower()

        # Simple keyword matching
        if any(word in desc_lower for word in ['salary', 'payroll', 'wages']):
            return 'Salaries'
        elif any(word in desc_lower for word in ['rent', 'lease', 'office']):
            return 'Rent'
        elif any(word in desc_lower for word in ['software', 'subscription', 'saas']):
            return 'Software'
        elif any(word in desc_lower for word in ['marketing', 'advertising', 'ads']):
            return 'Marketing'
        elif any(word in desc_lower for word in ['travel', 'flight', 'hotel']):
            return 'Travel'
        elif any(word in desc_lower for word in ['supplies', 'equipment']):
            return 'Supplies'
        elif any(word in desc_lower for word in ['utilities', 'electricity', 'water']):
            return 'Utilities'
        elif any(word in desc_lower for word in ['insurance']):
            return 'Insurance'
        else:
            return 'Other'

    def _record_transaction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Record a financial transaction."""
        import uuid

        transaction = {
            'transaction_id': str(uuid.uuid4()),
            'type': data.get('type', 'expense'),
            'amount': data.get('amount', 0),
            'description': data.get('description', ''),
            'category': data.get('category', 'Other'),
            'date': data.get('date', datetime.now().isoformat()),
            'recorded_at': datetime.now().isoformat()
        }

        self.transactions.append(transaction)

        # Save to disk
        self._save_transactions()

        logger.info(f"Transaction recorded: {transaction['transaction_id']}")

        return {
            'success': True,
            'transaction_id': transaction['transaction_id'],
            'recorded': True,
            'transaction': transaction
        }

    def _generate_financial_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a financial report."""
        report_type = data.get('report_type', 'summary')
        start_date = data.get('start_date')
        end_date = data.get('end_date', datetime.now().isoformat())

        # Filter transactions by date range
        filtered_transactions = self._filter_transactions_by_date(
            start_date, end_date
        )

        if report_type == 'profit_loss':
            report = self._generate_profit_loss(filtered_transactions)
        elif report_type == 'balance_sheet':
            report = self._generate_balance_sheet(filtered_transactions)
        elif report_type == 'cash_flow':
            report = self._generate_cash_flow(filtered_transactions)
        else:
            report = self._generate_summary(filtered_transactions)

        return {
            'success': True,
            'report_type': report_type,
            'period': {
                'start': start_date,
                'end': end_date
            },
            'report': report
        }

    def _filter_transactions_by_date(
        self,
        start_date: Optional[str],
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Filter transactions by date range."""
        filtered = []

        for txn in self.transactions:
            txn_date = txn.get('date', '')
            if start_date and txn_date < start_date:
                continue
            if txn_date > end_date:
                continue
            filtered.append(txn)

        return filtered

    def _generate_profit_loss(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate profit & loss statement."""
        income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')

        # Group expenses by category
        expense_by_category = {}
        for txn in transactions:
            if txn['type'] == 'expense':
                category = txn.get('category', 'Other')
                expense_by_category[category] = expense_by_category.get(category, 0) + txn['amount']

        return {
            'total_income': income,
            'total_expenses': expenses,
            'net_profit': income - expenses,
            'expense_breakdown': expense_by_category,
            'profit_margin': (income - expenses) / income * 100 if income > 0 else 0
        }

    def _generate_balance_sheet(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate balance sheet."""
        # Simplified balance sheet
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        total_expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        cash = total_income - total_expenses

        return {
            'assets': {
                'cash': cash,
                'total': cash
            },
            'liabilities': {
                'total': 0
            },
            'equity': {
                'retained_earnings': cash,
                'total': cash
            }
        }

    def _generate_cash_flow(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate cash flow statement."""
        cash_inflows = sum(t['amount'] for t in transactions if t['type'] == 'income')
        cash_outflows = sum(t['amount'] for t in transactions if t['type'] == 'expense')

        return {
            'operating_activities': {
                'cash_inflows': cash_inflows,
                'cash_outflows': cash_outflows,
                'net_cash_flow': cash_inflows - cash_outflows
            },
            'investing_activities': {
                'net_cash_flow': 0
            },
            'financing_activities': {
                'net_cash_flow': 0
            },
            'net_change_in_cash': cash_inflows - cash_outflows
        }

    def _generate_summary(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate financial summary."""
        income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')

        return {
            'total_transactions': len(transactions),
            'total_income': income,
            'total_expenses': expenses,
            'net': income - expenses,
            'average_transaction': (income + expenses) / len(transactions) if transactions else 0
        }

    def _analyze_spending(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze spending patterns."""
        period_days = data.get('period_days', 30)
        category = data.get('category')

        # Get transactions for period
        cutoff_date = (datetime.now() - timedelta(days=period_days)).isoformat()
        recent_transactions = [
            t for t in self.transactions
            if t.get('date', '') >= cutoff_date and t['type'] == 'expense'
        ]

        # Filter by category if specified
        if category:
            recent_transactions = [
                t for t in recent_transactions
                if t.get('category') == category
            ]

        # Calculate statistics
        total_spent = sum(t['amount'] for t in recent_transactions)
        avg_transaction = total_spent / len(recent_transactions) if recent_transactions else 0

        # Group by category
        by_category = {}
        for txn in recent_transactions:
            cat = txn.get('category', 'Other')
            by_category[cat] = by_category.get(cat, 0) + txn['amount']

        # Find top categories
        top_categories = sorted(
            by_category.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return {
            'success': True,
            'period_days': period_days,
            'total_spent': total_spent,
            'transaction_count': len(recent_transactions),
            'average_transaction': avg_transaction,
            'spending_by_category': by_category,
            'top_categories': [
                {'category': cat, 'amount': amt, 'percentage': amt / total_spent * 100}
                for cat, amt in top_categories
            ] if total_spent > 0 else []
        }

    def _check_budget(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check budget status."""
        category = data.get('category', 'total')
        period = data.get('period', 'monthly')

        # Get budget for category
        budget_key = f"{category}_{period}"
        budget = self.budgets.get(budget_key, {})

        if not budget:
            return {
                'success': False,
                'message': f"No budget set for {category} ({period})"
            }

        # Calculate spending for period
        period_days = 30 if period == 'monthly' else 7 if period == 'weekly' else 365
        cutoff_date = (datetime.now() - timedelta(days=period_days)).isoformat()

        spent = sum(
            t['amount'] for t in self.transactions
            if t['type'] == 'expense'
            and t.get('date', '') >= cutoff_date
            and (category == 'total' or t.get('category') == category)
        )

        budget_amount = budget.get('amount', 0)
        remaining = budget_amount - spent
        percentage_used = (spent / budget_amount * 100) if budget_amount > 0 else 0

        # Determine status
        if percentage_used >= 100:
            status = 'over_budget'
        elif percentage_used >= 90:
            status = 'warning'
        elif percentage_used >= 75:
            status = 'caution'
        else:
            status = 'on_track'

        return {
            'success': True,
            'category': category,
            'period': period,
            'budget': budget_amount,
            'spent': spent,
            'remaining': remaining,
            'percentage_used': percentage_used,
            'status': status
        }

    def _reconcile_accounts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reconcile bank accounts."""
        account_id = data.get('account_id')
        statement_date = data.get('statement_date', datetime.now().isoformat())

        # This would integrate with actual bank data
        # For now, return a simplified reconciliation

        return {
            'success': True,
            'account_id': account_id,
            'statement_date': statement_date,
            'reconciliation': {
                'matched_transactions': 0,
                'unmatched_transactions': 0,
                'discrepancies': [],
                'status': 'pending_review'
            },
            'requires_human_review': True
        }

    def _save_transactions(self) -> None:
        """Save transactions to disk."""
        import json
        transactions_path = self.agent_dir / "transactions.json"
        try:
            with open(transactions_path, 'w') as f:
                json.dump(self.transactions, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving transactions: {e}")

    def _load_transactions(self) -> None:
        """Load transactions from disk."""
        import json
        transactions_path = self.agent_dir / "transactions.json"
        if transactions_path.exists():
            try:
                with open(transactions_path, 'r') as f:
                    self.transactions = json.load(f)
                logger.info(f"Loaded {len(self.transactions)} transactions")
            except Exception as e:
                logger.error(f"Error loading transactions: {e}")


def main():
    """Main function for testing financial agent."""
    import argparse

    parser = argparse.ArgumentParser(description='Financial Agent')
    parser.add_argument('--vault-path', default='AI_Employee_Vault', help='Path to AI Employee Vault')
    parser.add_argument('--test', action='store_true', help='Run test scenarios')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize agent
    agent = FinancialAgent(args.vault_path)

    if args.test:
        print("Testing Financial Agent...")
        print("=" * 80)

        # Test 1: Categorize expense
        print("\nTest 1: Categorize Expense")
        task = AgentTask(
            task_id="test_1",
            task_type="categorize_expense",
            description="Categorize office rent expense",
            priority=TaskPriority.MEDIUM,
            assigned_to=agent.agent_id,
            assigned_by=None,
            created_at=datetime.now().isoformat(),
            metadata={
                'description': 'Monthly office rent payment',
                'amount': 2500.00,
                'vendor': 'Property Management Co'
            }
        )
        result = agent.process_task(task)
        print(f"  Category: {result['category']}")
        print(f"  Confidence: {result['confidence']:.2f}")

        # Test 2: Record transaction
        print("\nTest 2: Record Transaction")
        task = AgentTask(
            task_id="test_2",
            task_type="record_transaction",
            description="Record software subscription",
            priority=TaskPriority.MEDIUM,
            assigned_to=agent.agent_id,
            assigned_by=None,
            created_at=datetime.now().isoformat(),
            metadata={
                'type': 'expense',
                'amount': 99.00,
                'description': 'Monthly SaaS subscription',
                'category': 'Software'
            }
        )
        result = agent.process_task(task)
        print(f"  Transaction ID: {result['transaction_id']}")
        print(f"  Recorded: {result['recorded']}")

        # Test 3: Generate financial report
        print("\nTest 3: Generate Financial Report")
        task = AgentTask(
            task_id="test_3",
            task_type="generate_financial_report",
            description="Generate summary report",
            priority=TaskPriority.MEDIUM,
            assigned_to=agent.agent_id,
            assigned_by=None,
            created_at=datetime.now().isoformat(),
            metadata={
                'report_type': 'summary'
            }
        )
        result = agent.process_task(task)
        print(f"  Report Type: {result['report_type']}")
        print(f"  Total Transactions: {result['report']['total_transactions']}")

        # Test 4: Agent status
        print("\nTest 4: Agent Status")
        status = agent.get_status()
        print(f"  Agent ID: {status['agent_id']}")
        print(f"  Role: {status['role']}")
        print(f"  Status: {status['status']}")
        print(f"  Capabilities: {len(status['capabilities'])}")

    else:
        print("Financial Agent initialized")
        print(f"Agent ID: {agent.agent_id}")
        print(f"Role: {agent.role.value}")
        print(f"Capabilities: {len(agent.capabilities)}")


if __name__ == '__main__':
    main()
