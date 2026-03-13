#!/usr/bin/env python3
"""
Odoo MCP Server - Financial Management Integration
Provides accounting tools for the Personal AI Employee system.
"""

import json
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import xmlrpc.client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OdooMCPServer:
    """MCP Server for Odoo accounting integration."""

    def __init__(self, url: str, db: str, username: str, password: str):
        """Initialize Odoo connection."""
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.models = None

        # Connect to Odoo
        self._connect()

    def _connect(self):
        """Establish connection to Odoo."""
        try:
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = common.authenticate(self.db, self.username, self.password, {})

            if not self.uid:
                raise Exception("Authentication failed")

            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            logger.info(f"Connected to Odoo as user ID: {self.uid}")

        except Exception as e:
            logger.error(f"Failed to connect to Odoo: {e}")
            raise

    def _execute(self, model: str, method: str, *args, **kwargs):
        """Execute Odoo model method."""
        try:
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, method, args, kwargs
            )
        except Exception as e:
            logger.error(f"Odoo execution error: {e}")
            raise

    # Tool 1: Get Account Balance
    def get_account_balance(self, account_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current balance for accounts.

        Args:
            account_code: Specific account code (e.g., '100000' for bank)
                         If None, returns all accounts

        Returns:
            Dictionary with account balances
        """
        try:
            domain = [('deprecated', '=', False)]
            if account_code:
                domain.append(('code', '=', account_code))

            accounts = self._execute(
                'account.account', 'search_read',
                domain,
                {'fields': ['code', 'name', 'balance', 'currency_id']}
            )

            result = {
                'timestamp': datetime.now().isoformat(),
                'accounts': []
            }

            for account in accounts:
                result['accounts'].append({
                    'code': account['code'],
                    'name': account['name'],
                    'balance': account['balance'],
                    'currency': account.get('currency_id', [False, 'USD'])[1]
                })

            return result

        except Exception as e:
            return {'error': str(e)}

    # Tool 2: Create Invoice
    def create_invoice(self, partner_name: str, amount: float,
                      description: str, invoice_type: str = 'out_invoice') -> Dict[str, Any]:
        """
        Create a new invoice (requires approval).

        Args:
            partner_name: Customer/vendor name
            amount: Invoice amount
            description: Invoice description
            invoice_type: 'out_invoice' (customer) or 'in_invoice' (vendor)

        Returns:
            Invoice details and approval request
        """
        try:
            # Find or create partner
            partner_ids = self._execute(
                'res.partner', 'search',
                [('name', '=', partner_name)]
            )

            if not partner_ids:
                return {
                    'status': 'approval_required',
                    'message': f'Partner "{partner_name}" not found. Create new partner?',
                    'action': 'create_partner',
                    'data': {
                        'partner_name': partner_name,
                        'amount': amount,
                        'description': description,
                        'invoice_type': invoice_type
                    }
                }

            partner_id = partner_ids[0]

            # Create invoice (draft state)
            invoice_data = {
                'partner_id': partner_id,
                'move_type': invoice_type,
                'invoice_date': datetime.now().strftime('%Y-%m-%d'),
                'invoice_line_ids': [(0, 0, {
                    'name': description,
                    'quantity': 1,
                    'price_unit': amount,
                })]
            }

            invoice_id = self._execute(
                'account.move', 'create',
                [invoice_data]
            )

            return {
                'status': 'created',
                'invoice_id': invoice_id,
                'partner': partner_name,
                'amount': amount,
                'type': invoice_type,
                'state': 'draft',
                'message': 'Invoice created in draft state. Requires approval to post.'
            }

        except Exception as e:
            return {'error': str(e)}

    # Tool 3: Record Payment
    def record_payment(self, invoice_id: int, amount: float,
                      payment_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Record payment for an invoice.

        Args:
            invoice_id: Odoo invoice ID
            amount: Payment amount
            payment_date: Payment date (YYYY-MM-DD), defaults to today

        Returns:
            Payment details
        """
        try:
            if not payment_date:
                payment_date = datetime.now().strftime('%Y-%m-%d')

            # Get invoice details
            invoice = self._execute(
                'account.move', 'read',
                [invoice_id],
                {'fields': ['name', 'partner_id', 'amount_total', 'state']}
            )[0]

            if invoice['state'] != 'posted':
                return {
                    'status': 'error',
                    'message': 'Invoice must be posted before recording payment'
                }

            # Create payment
            payment_data = {
                'payment_type': 'inbound' if invoice['move_type'] == 'out_invoice' else 'outbound',
                'partner_id': invoice['partner_id'][0],
                'amount': amount,
                'date': payment_date,
                'ref': f"Payment for {invoice['name']}"
            }

            payment_id = self._execute(
                'account.payment', 'create',
                [payment_data]
            )

            # Post payment
            self._execute(
                'account.payment', 'action_post',
                [payment_id]
            )

            return {
                'status': 'success',
                'payment_id': payment_id,
                'invoice': invoice['name'],
                'amount': amount,
                'date': payment_date
            }

        except Exception as e:
            return {'error': str(e)}

    # Tool 4: Get Financial Report
    def get_financial_report(self, report_type: str,
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate financial report.

        Args:
            report_type: 'profit_loss', 'balance_sheet', or 'cash_flow'
            start_date: Report start date (YYYY-MM-DD)
            end_date: Report end date (YYYY-MM-DD)

        Returns:
            Financial report data
        """
        try:
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

            if report_type == 'profit_loss':
                return self._get_profit_loss(start_date, end_date)
            elif report_type == 'balance_sheet':
                return self._get_balance_sheet(end_date)
            elif report_type == 'cash_flow':
                return self._get_cash_flow(start_date, end_date)
            else:
                return {'error': f'Unknown report type: {report_type}'}

        except Exception as e:
            return {'error': str(e)}

    def _get_profit_loss(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get profit & loss statement."""
        # Get income accounts
        income_accounts = self._execute(
            'account.account', 'search_read',
            [('user_type_id.name', '=', 'Income')],
            {'fields': ['code', 'name', 'balance']}
        )

        # Get expense accounts
        expense_accounts = self._execute(
            'account.account', 'search_read',
            [('user_type_id.name', '=', 'Expenses')],
            {'fields': ['code', 'name', 'balance']}
        )

        total_income = sum(acc['balance'] for acc in income_accounts)
        total_expenses = sum(acc['balance'] for acc in expense_accounts)
        net_profit = total_income - total_expenses

        return {
            'report_type': 'profit_loss',
            'period': f'{start_date} to {end_date}',
            'income': {
                'accounts': income_accounts,
                'total': total_income
            },
            'expenses': {
                'accounts': expense_accounts,
                'total': total_expenses
            },
            'net_profit': net_profit
        }

    def _get_balance_sheet(self, date: str) -> Dict[str, Any]:
        """Get balance sheet."""
        # Get assets
        assets = self._execute(
            'account.account', 'search_read',
            [('user_type_id.name', 'in', ['Current Assets', 'Fixed Assets'])],
            {'fields': ['code', 'name', 'balance']}
        )

        # Get liabilities
        liabilities = self._execute(
            'account.account', 'search_read',
            [('user_type_id.name', 'in', ['Current Liabilities', 'Non-current Liabilities'])],
            {'fields': ['code', 'name', 'balance']}
        )

        # Get equity
        equity = self._execute(
            'account.account', 'search_read',
            [('user_type_id.name', '=', 'Equity')],
            {'fields': ['code', 'name', 'balance']}
        )

        total_assets = sum(acc['balance'] for acc in assets)
        total_liabilities = sum(acc['balance'] for acc in liabilities)
        total_equity = sum(acc['balance'] for acc in equity)

        return {
            'report_type': 'balance_sheet',
            'date': date,
            'assets': {
                'accounts': assets,
                'total': total_assets
            },
            'liabilities': {
                'accounts': liabilities,
                'total': total_liabilities
            },
            'equity': {
                'accounts': equity,
                'total': total_equity
            },
            'balance_check': total_assets - (total_liabilities + total_equity)
        }

    def _get_cash_flow(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get cash flow statement."""
        # Get cash accounts
        cash_accounts = self._execute(
            'account.account', 'search_read',
            [('user_type_id.name', '=', 'Bank and Cash')],
            {'fields': ['code', 'name', 'balance']}
        )

        # Get account moves for the period
        moves = self._execute(
            'account.move.line', 'search_read',
            [
                ('account_id.user_type_id.name', '=', 'Bank and Cash'),
                ('date', '>=', start_date),
                ('date', '<=', end_date)
            ],
            {'fields': ['date', 'name', 'debit', 'credit', 'balance']}
        )

        total_inflow = sum(move['debit'] for move in moves)
        total_outflow = sum(move['credit'] for move in moves)
        net_cash_flow = total_inflow - total_outflow

        return {
            'report_type': 'cash_flow',
            'period': f'{start_date} to {end_date}',
            'cash_accounts': cash_accounts,
            'inflows': total_inflow,
            'outflows': total_outflow,
            'net_cash_flow': net_cash_flow,
            'transactions': len(moves)
        }

    # Tool 5: Search Transactions
    def search_transactions(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search accounting transactions.

        Args:
            query: Search query (partner name, reference, etc.)
            limit: Maximum results to return

        Returns:
            List of matching transactions
        """
        try:
            # Search in account moves
            moves = self._execute(
                'account.move', 'search_read',
                [
                    '|', '|',
                    ('name', 'ilike', query),
                    ('ref', 'ilike', query),
                    ('partner_id.name', 'ilike', query)
                ],
                {
                    'fields': ['name', 'date', 'partner_id', 'amount_total', 'state', 'move_type'],
                    'limit': limit
                }
            )

            results = []
            for move in moves:
                results.append({
                    'id': move['id'],
                    'reference': move['name'],
                    'date': move['date'],
                    'partner': move.get('partner_id', [False, 'N/A'])[1],
                    'amount': move['amount_total'],
                    'state': move['state'],
                    'type': move['move_type']
                })

            return {
                'query': query,
                'results': results,
                'count': len(results)
            }

        except Exception as e:
            return {'error': str(e)}


def handle_mcp_request(server: OdooMCPServer, request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP tool request."""
    tool = request.get('tool')
    params = request.get('params', {})

    if tool == 'get_account_balance':
        return server.get_account_balance(params.get('account_code'))

    elif tool == 'create_invoice':
        return server.create_invoice(
            params['partner_name'],
            params['amount'],
            params['description'],
            params.get('invoice_type', 'out_invoice')
        )

    elif tool == 'record_payment':
        return server.record_payment(
            params['invoice_id'],
            params['amount'],
            params.get('payment_date')
        )

    elif tool == 'get_financial_report':
        return server.get_financial_report(
            params['report_type'],
            params.get('start_date'),
            params.get('end_date')
        )

    elif tool == 'search_transactions':
        return server.search_transactions(
            params['query'],
            params.get('limit', 10)
        )

    else:
        return {'error': f'Unknown tool: {tool}'}


def main():
    """Main MCP server loop."""
    # Load configuration
    config_path = Path(__file__).parent.parent / 'AI_Employee_Vault' / 'Config' / 'odoo_config.json'

    if not config_path.exists():
        print(json.dumps({
            'error': 'Odoo configuration not found',
            'message': 'Create AI_Employee_Vault/Config/odoo_config.json with Odoo credentials'
        }))
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    # Initialize server
    try:
        server = OdooMCPServer(
            config['url'],
            config['database'],
            config['username'],
            config['password']
        )
    except Exception as e:
        print(json.dumps({'error': f'Failed to connect to Odoo: {e}'}))
        sys.exit(1)

    # MCP server loop
    logger.info("Odoo MCP Server started")

    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = handle_mcp_request(server, request)
            print(json.dumps(response))
            sys.stdout.flush()
        except json.JSONDecodeError:
            print(json.dumps({'error': 'Invalid JSON request'}))
        except Exception as e:
            print(json.dumps({'error': str(e)}))


if __name__ == '__main__':
    main()
