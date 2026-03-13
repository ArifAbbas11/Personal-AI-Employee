#!/usr/bin/env python3
"""
Financial Data Collector for CEO Briefing
Collects financial metrics from Odoo for weekly executive reports.
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinancialDataCollector:
    """Collects financial data from Odoo for CEO Briefing."""

    def __init__(self, vault_path: str):
        """Initialize collector."""
        self.vault = Path(vault_path)
        self.config_path = self.vault / 'Config' / 'odoo_config.json'
        self.mcp_server_path = Path(__file__).parent.parent / 'watchers' / 'odoo_mcp_server.py'
        self.odoo_available = self._check_odoo_availability()

    def _check_odoo_availability(self) -> bool:
        """Check if Odoo is configured and available."""
        if not self.config_path.exists():
            logger.warning("Odoo config not found - financial data will be unavailable")
            return False

        try:
            # Try to load config
            with open(self.config_path) as f:
                config = json.load(f)

            # Check required fields
            required = ['url', 'database', 'username', 'password']
            if not all(field in config for field in required):
                logger.warning("Odoo config incomplete - financial data will be unavailable")
                return False

            return True

        except Exception as e:
            logger.warning(f"Odoo config error: {e}")
            return False

    def _call_odoo_tool(self, tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call Odoo MCP server tool."""
        if not self.odoo_available:
            return {'error': 'Odoo not available'}

        try:
            request = json.dumps({'tool': tool, 'params': params})

            result = subprocess.run(
                ['python3', str(self.mcp_server_path)],
                input=request + '\n',
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return {'error': f'MCP server error: {result.stderr}'}

            response = json.loads(result.stdout.strip())
            return response

        except subprocess.TimeoutExpired:
            return {'error': 'Odoo request timeout'}
        except Exception as e:
            return {'error': str(e)}

    def collect_weekly_data(self, start_date: datetime.date, end_date: datetime.date) -> Dict[str, Any]:
        """
        Collect financial data for the week.

        Args:
            start_date: Week start date
            end_date: Week end date

        Returns:
            Dictionary with financial metrics
        """
        if not self.odoo_available:
            return {
                'available': False,
                'message': 'Odoo not configured - install and configure Odoo for financial data'
            }

        try:
            # Get profit & loss for the week
            pl_report = self._call_odoo_tool('get_financial_report', {
                'report_type': 'profit_loss',
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            })

            # Get cash flow for the week
            cf_report = self._call_odoo_tool('get_financial_report', {
                'report_type': 'cash_flow',
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            })

            # Get current account balances
            balances = self._call_odoo_tool('get_account_balance', {})

            # Get outstanding invoices
            outstanding = self._get_outstanding_invoices()

            # Calculate key metrics
            metrics = self._calculate_metrics(pl_report, cf_report, balances, outstanding)

            return {
                'available': True,
                'period': f'{start_date} to {end_date}',
                'profit_loss': self._format_profit_loss(pl_report),
                'cash_flow': self._format_cash_flow(cf_report),
                'balances': self._format_balances(balances),
                'outstanding_invoices': outstanding,
                'metrics': metrics
            }

        except Exception as e:
            logger.error(f"Error collecting financial data: {e}")
            return {
                'available': False,
                'error': str(e)
            }

    def _get_outstanding_invoices(self) -> Dict[str, Any]:
        """Get outstanding invoices (unpaid)."""
        try:
            # Search for posted invoices that are not paid
            result = self._call_odoo_tool('search_transactions', {
                'query': 'state:posted',
                'limit': 100
            })

            if 'error' in result:
                return {'count': 0, 'total': 0, 'invoices': []}

            # Filter for unpaid invoices
            outstanding = []
            total_outstanding = 0

            for invoice in result.get('results', []):
                if invoice.get('state') == 'posted':
                    outstanding.append({
                        'reference': invoice['reference'],
                        'partner': invoice['partner'],
                        'amount': invoice['amount'],
                        'date': invoice['date']
                    })
                    total_outstanding += invoice['amount']

            return {
                'count': len(outstanding),
                'total': total_outstanding,
                'invoices': outstanding[:10]  # Top 10 for briefing
            }

        except Exception as e:
            logger.error(f"Error getting outstanding invoices: {e}")
            return {'count': 0, 'total': 0, 'invoices': []}

    def _format_profit_loss(self, pl_report: Dict[str, Any]) -> Dict[str, Any]:
        """Format profit & loss data for briefing."""
        if 'error' in pl_report:
            return {'available': False, 'error': pl_report['error']}

        return {
            'available': True,
            'revenue': pl_report.get('income', {}).get('total', 0),
            'expenses': pl_report.get('expenses', {}).get('total', 0),
            'net_profit': pl_report.get('net_profit', 0),
            'profit_margin': self._calculate_profit_margin(
                pl_report.get('income', {}).get('total', 0),
                pl_report.get('net_profit', 0)
            )
        }

    def _format_cash_flow(self, cf_report: Dict[str, Any]) -> Dict[str, Any]:
        """Format cash flow data for briefing."""
        if 'error' in cf_report:
            return {'available': False, 'error': cf_report['error']}

        return {
            'available': True,
            'inflows': cf_report.get('inflows', 0),
            'outflows': cf_report.get('outflows', 0),
            'net_cash_flow': cf_report.get('net_cash_flow', 0),
            'transactions': cf_report.get('transactions', 0)
        }

    def _format_balances(self, balances: Dict[str, Any]) -> Dict[str, Any]:
        """Format account balances for briefing."""
        if 'error' in balances:
            return {'available': False, 'error': balances['error']}

        # Extract key accounts
        accounts = balances.get('accounts', [])

        # Find bank/cash accounts
        cash_balance = sum(
            acc['balance'] for acc in accounts
            if 'bank' in acc['name'].lower() or 'cash' in acc['name'].lower()
        )

        # Find receivables
        receivables = sum(
            acc['balance'] for acc in accounts
            if 'receivable' in acc['name'].lower()
        )

        # Find payables
        payables = sum(
            acc['balance'] for acc in accounts
            if 'payable' in acc['name'].lower()
        )

        return {
            'available': True,
            'cash': cash_balance,
            'receivables': receivables,
            'payables': payables,
            'working_capital': cash_balance + receivables - payables
        }

    def _calculate_metrics(self, pl_report: Dict, cf_report: Dict,
                          balances: Dict, outstanding: Dict) -> Dict[str, Any]:
        """Calculate key financial metrics."""
        metrics = {}

        # Revenue metrics
        if 'error' not in pl_report:
            revenue = pl_report.get('income', {}).get('total', 0)
            net_profit = pl_report.get('net_profit', 0)

            metrics['revenue'] = revenue
            metrics['profit_margin'] = self._calculate_profit_margin(revenue, net_profit)

        # Cash metrics
        if 'error' not in cf_report:
            metrics['cash_flow'] = cf_report.get('net_cash_flow', 0)

        # Balance metrics
        if 'error' not in balances:
            accounts = balances.get('accounts', [])
            cash = sum(
                acc['balance'] for acc in accounts
                if 'bank' in acc['name'].lower() or 'cash' in acc['name'].lower()
            )
            metrics['cash_position'] = cash

        # Collection metrics
        if outstanding.get('count', 0) > 0:
            metrics['outstanding_invoices'] = outstanding['count']
            metrics['outstanding_amount'] = outstanding['total']

        return metrics

    def _calculate_profit_margin(self, revenue: float, net_profit: float) -> float:
        """Calculate profit margin percentage."""
        if revenue == 0:
            return 0.0
        return (net_profit / revenue) * 100

    def get_monthly_summary(self) -> Dict[str, Any]:
        """Get monthly financial summary for dashboard."""
        if not self.odoo_available:
            return {'available': False}

        try:
            end_date = datetime.now().date()
            start_date = end_date.replace(day=1)  # First day of month

            # Get monthly P&L
            pl_report = self._call_odoo_tool('get_financial_report', {
                'report_type': 'profit_loss',
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            })

            # Get balance sheet
            bs_report = self._call_odoo_tool('get_financial_report', {
                'report_type': 'balance_sheet',
                'end_date': end_date.strftime('%Y-%m-%d')
            })

            return {
                'available': True,
                'month': start_date.strftime('%B %Y'),
                'revenue': pl_report.get('income', {}).get('total', 0),
                'expenses': pl_report.get('expenses', {}).get('total', 0),
                'net_profit': pl_report.get('net_profit', 0),
                'total_assets': bs_report.get('assets', {}).get('total', 0),
                'total_liabilities': bs_report.get('liabilities', {}).get('total', 0)
            }

        except Exception as e:
            logger.error(f"Error getting monthly summary: {e}")
            return {'available': False, 'error': str(e)}


def main():
    """Test the financial data collector."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python financial_collector.py <vault_path>")
        sys.exit(1)

    vault_path = sys.argv[1]
    collector = FinancialDataCollector(vault_path)

    # Test weekly data collection
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)

    print("Collecting financial data...")
    data = collector.collect_weekly_data(start_date, end_date)

    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
