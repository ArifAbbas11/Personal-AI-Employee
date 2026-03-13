#!/usr/bin/env python3
"""
Production Workflow: Daily Expense Processing
Processes expenses from CSV file and generates categorized report
"""

import sys
import csv
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent / "watchers"))

from multi_agent.base import AgentCoordinator, TaskPriority
from multi_agent.financial_agent import FinancialAgent


def process_expense_file(csv_file: str) -> Dict:
    """Process expenses from CSV file"""
    
    coordinator = AgentCoordinator("AI_Employee_Vault")
    financial = FinancialAgent("AI_Employee_Vault", coordinator)
    
    # Read expenses from CSV
    expenses = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        expenses = list(reader)
    
    if not expenses:
        return {'error': 'No expenses found in file'}
    
    # Process each expense
    results = []
    total_amount = 0
    category_totals = {}
    
    print(f"\n{'='*80}")
    print(f"DAILY EXPENSE PROCESSING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    print(f"\nProcessing {len(expenses)} expenses from {csv_file}\n")
    
    for i, expense in enumerate(expenses, 1):
        # Validate required fields
        if 'description' not in expense or 'amount' not in expense:
            print(f"⚠️  Skipping row {i}: Missing required fields")
            continue
        
        try:
            amount = float(expense['amount'])
        except ValueError:
            print(f"⚠️  Skipping row {i}: Invalid amount '{expense['amount']}'")
            continue
        
        # Process expense
        task = coordinator.delegate_task(
            task_type="categorize_expense",
            description=f"Categorize: {expense['description']}",
            priority=TaskPriority.MEDIUM,
            metadata={
                'description': expense['description'],
                'amount': amount,
                'vendor': expense.get('vendor', 'Unknown'),
                'date': expense.get('date', datetime.now().strftime('%Y-%m-%d'))
            }
        )
        
        result = financial.process_task(task)
        category = result['category']
        confidence = result['confidence']
        
        # Track totals
        total_amount += amount
        category_totals[category] = category_totals.get(category, 0) + amount
        
        # Store result
        results.append({
            **expense,
            'amount': amount,
            'category': category,
            'confidence': confidence,
            'processed_at': datetime.now().isoformat()
        })
        
        # Print progress
        print(f"{i:3d}. ${amount:>9.2f} - {expense['description'][:50]}")
        print(f"     → {category} ({confidence:.1%})")
    
    # Generate summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"\nTotal Expenses: {len(results)}")
    print(f"Total Amount: ${total_amount:,.2f}\n")
    
    print("By Category:")
    for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
        percentage = (amount / total_amount) * 100
        print(f"  {category:20s}: ${amount:>10.2f} ({percentage:>5.1f}%)")
    
    # Save results
    output_file = f"expense_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_path = Path(__file__).parent.parent / "AI_Employee_Vault" / "Done" / output_file
    
    report = {
        'processed_at': datetime.now().isoformat(),
        'source_file': csv_file,
        'total_expenses': len(results),
        'total_amount': total_amount,
        'category_totals': category_totals,
        'expenses': results
    }
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Report saved to: {output_path}")
    print(f"{'='*80}\n")
    
    return report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python daily_expense_processor.py <expenses.csv>")
        print("\nCSV format:")
        print("  description,amount,vendor,date")
        print("  Office supplies,45.99,Staples,2026-03-03")
        print("  AWS hosting,1250.00,AWS,2026-03-03")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    if not Path(csv_file).exists():
        print(f"❌ Error: File not found: {csv_file}")
        sys.exit(1)
    
    process_expense_file(csv_file)
