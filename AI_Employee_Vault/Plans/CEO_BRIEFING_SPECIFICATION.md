# CEO Briefing System Specification

---
created: 2026-02-26
component: ceo-briefing-generator
status: specification
tier: gold
---

## Overview

The CEO Briefing System autonomously generates weekly business intelligence reports that provide executive-level insights into business performance, identify bottlenecks, and offer proactive recommendations. This transforms the AI Employee from a reactive assistant into a proactive business partner.

## Purpose

Generate a comprehensive weekly briefing every Monday morning that answers:
- How is the business performing financially?
- What tasks were completed vs planned?
- Where are the bottlenecks?
- What proactive actions should be taken?
- What's coming up this week?

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Data Sources                                       │
├─────────────────────────────────────────────────────┤
│  • Odoo (Revenue, Expenses, Invoices)              │
│  • Email (Client communications)                    │
│  • Tasks (Completed, Pending, Bottlenecks)         │
│  • Social Media (Engagement metrics)                │
│  • Calendar (Time allocation)                       │
│  • Logs (System activity)                           │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  Data Aggregation Layer                             │
│  (ceo_briefing_generator.py)                        │
├─────────────────────────────────────────────────────┤
│  • Collect data from all sources                    │
│  • Calculate metrics and trends                     │
│  • Identify patterns and anomalies                  │
│  • Generate insights                                │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  Analysis Engine                                    │
├─────────────────────────────────────────────────────┤
│  • Revenue trend analysis                           │
│  • Expense categorization                           │
│  • Bottleneck detection                             │
│  • Subscription waste detection                     │
│  • Client health scoring                            │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  Report Generation                                  │
├─────────────────────────────────────────────────────┤
│  • Executive summary                                │
│  • Financial performance                            │
│  • Task completion analysis                         │
│  • Proactive recommendations                        │
│  • Upcoming deadlines                               │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  Output                                             │
│  /Briefings/YYYY-MM-DD_Monday_Briefing.md          │
└─────────────────────────────────────────────────────┘
```

## Implementation

### Component 1: Data Collectors

**Location:** `watchers/data_collectors/`

```python
# watchers/data_collectors/financial_collector.py
"""Collect financial data from Odoo"""

from pathlib import Path
import json
from datetime import datetime, timedelta

class FinancialDataCollector:
    def __init__(self, odoo_client, vault_path):
        self.odoo = odoo_client
        self.vault = Path(vault_path)

    def collect_weekly_data(self, start_date, end_date):
        """Collect financial data for the week"""

        # Get revenue (posted invoices)
        revenue_data = self.odoo.search(
            'account.move',
            [
                ['move_type', '=', 'out_invoice'],
                ['state', '=', 'posted'],
                ['invoice_date', '>=', start_date],
                ['invoice_date', '<=', end_date]
            ],
            ['name', 'partner_id', 'amount_total', 'invoice_date']
        )

        total_revenue = sum(inv['amount_total'] for inv in revenue_data)

        # Get expenses
        expense_data = self.odoo.search(
            'account.move',
            [
                ['move_type', '=', 'in_invoice'],
                ['state', '=', 'posted'],
                ['invoice_date', '>=', start_date],
                ['invoice_date', '<=', end_date]
            ],
            ['name', 'partner_id', 'amount_total', 'invoice_date']
        )

        total_expenses = sum(exp['amount_total'] for exp in expense_data)

        # Get unpaid invoices
        unpaid_invoices = self.odoo.search(
            'account.move',
            [
                ['move_type', '=', 'out_invoice'],
                ['state', '=', 'posted'],
                ['payment_state', 'in', ['not_paid', 'partial']]
            ],
            ['name', 'partner_id', 'amount_residual', 'invoice_date_due']
        )

        # Calculate overdue
        today = datetime.now().date()
        overdue_invoices = [
            inv for inv in unpaid_invoices
            if datetime.strptime(inv['invoice_date_due'], '%Y-%m-%d').date() < today
        ]

        return {
            'revenue': {
                'total': total_revenue,
                'count': len(revenue_data),
                'invoices': revenue_data
            },
            'expenses': {
                'total': total_expenses,
                'count': len(expense_data),
                'items': expense_data
            },
            'receivables': {
                'total_outstanding': sum(inv['amount_residual'] for inv in unpaid_invoices),
                'count': len(unpaid_invoices),
                'overdue_count': len(overdue_invoices),
                'overdue_amount': sum(inv['amount_residual'] for inv in overdue_invoices)
            }
        }
```

```python
# watchers/data_collectors/task_collector.py
"""Collect task completion data"""

from pathlib import Path
from datetime import datetime, timedelta
import frontmatter

class TaskDataCollector:
    def __init__(self, vault_path):
        self.vault = Path(vault_path)
        self.done = self.vault / 'Done'
        self.needs_action = self.vault / 'Needs_Action'

    def collect_weekly_data(self, start_date, end_date):
        """Collect task data for the week"""

        completed_tasks = []

        # Scan Done folder for tasks completed this week
        for task_file in self.done.glob('*.md'):
            try:
                stat = task_file.stat()
                modified_time = datetime.fromtimestamp(stat.st_mtime)

                if start_date <= modified_time.date() <= end_date:
                    # Parse frontmatter
                    with open(task_file, 'r') as f:
                        post = frontmatter.load(f)

                    completed_tasks.append({
                        'name': task_file.stem,
                        'type': post.get('type', 'unknown'),
                        'completed_date': modified_time.isoformat(),
                        'priority': post.get('priority', 'medium')
                    })
            except Exception as e:
                continue

        # Get pending tasks
        pending_tasks = []
        for task_file in self.needs_action.glob('*.md'):
            try:
                with open(task_file, 'r') as f:
                    post = frontmatter.load(f)

                pending_tasks.append({
                    'name': task_file.stem,
                    'type': post.get('type', 'unknown'),
                    'priority': post.get('priority', 'medium'),
                    'age_days': (datetime.now() - datetime.fromtimestamp(task_file.stat().st_ctime)).days
                })
            except Exception as e:
                continue

        # Detect bottlenecks (tasks pending > 3 days)
        bottlenecks = [t for t in pending_tasks if t['age_days'] > 3]

        return {
            'completed': {
                'count': len(completed_tasks),
                'tasks': completed_tasks
            },
            'pending': {
                'count': len(pending_tasks),
                'tasks': pending_tasks
            },
            'bottlenecks': {
                'count': len(bottlenecks),
                'tasks': bottlenecks
            }
        }
```

```python
# watchers/data_collectors/communication_collector.py
"""Collect communication metrics"""

from pathlib import Path
from datetime import datetime
import json

class CommunicationDataCollector:
    def __init__(self, vault_path):
        self.vault = Path(vault_path)
        self.logs = self.vault / 'Logs'

    def collect_weekly_data(self, start_date, end_date):
        """Collect communication data for the week"""

        emails_sent = 0
        emails_received = 0
        avg_response_time_hours = 0
        social_posts = 0

        # Parse logs for the week
        for log_file in self.logs.glob('*.json'):
            try:
                log_date = datetime.strptime(log_file.stem, '%Y-%m-%d').date()

                if start_date <= log_date <= end_date:
                    with open(log_file, 'r') as f:
                        logs = [json.loads(line) for line in f]

                    for log in logs:
                        if log.get('action_type') == 'email_send':
                            emails_sent += 1
                        elif log.get('action_type') == 'email_receive':
                            emails_received += 1
                        elif log.get('action_type') in ['linkedin_post', 'facebook_post', 'twitter_post']:
                            social_posts += 1
            except Exception as e:
                continue

        return {
            'emails': {
                'sent': emails_sent,
                'received': emails_received,
                'avg_response_time_hours': avg_response_time_hours
            },
            'social_media': {
                'posts': social_posts
            }
        }
```

### Component 2: Analysis Engine

```python
# watchers/analysis_engine.py
"""Analyze collected data and generate insights"""

from datetime import datetime, timedelta

class AnalysisEngine:
    def __init__(self, business_goals):
        self.goals = business_goals

    def analyze_financial_performance(self, financial_data, previous_week_data=None):
        """Analyze financial performance and trends"""

        revenue = financial_data['revenue']['total']
        expenses = financial_data['expenses']['total']
        net = revenue - expenses

        # Calculate trend
        trend = 'stable'
        if previous_week_data:
            prev_revenue = previous_week_data['revenue']['total']
            if revenue > prev_revenue * 1.1:
                trend = 'up'
            elif revenue < prev_revenue * 0.9:
                trend = 'down'

        # Check against goals
        monthly_goal = self.goals.get('monthly_revenue_target', 5000)
        mtd_revenue = self._get_mtd_revenue()
        progress_pct = (mtd_revenue / monthly_goal * 100) if monthly_goal > 0 else 0

        status = 'on_track' if progress_pct >= 25 else 'behind'  # Assuming week 1 of month

        return {
            'revenue': revenue,
            'expenses': expenses,
            'net': net,
            'trend': trend,
            'monthly_progress': {
                'current': mtd_revenue,
                'target': monthly_goal,
                'percentage': progress_pct,
                'status': status
            }
        }

    def detect_bottlenecks(self, task_data):
        """Identify task bottlenecks"""

        bottlenecks = []

        for task in task_data['bottlenecks']['tasks']:
            bottleneck = {
                'task': task['name'],
                'age_days': task['age_days'],
                'priority': task['priority'],
                'severity': 'high' if task['age_days'] > 7 else 'medium'
            }

            # Infer root cause
            if 'email' in task['name'].lower():
                bottleneck['likely_cause'] = 'Waiting on client response'
            elif 'approval' in task['name'].lower():
                bottleneck['likely_cause'] = 'Pending human approval'
            else:
                bottleneck['likely_cause'] = 'Unknown - requires investigation'

            bottlenecks.append(bottleneck)

        return bottlenecks

    def detect_subscription_waste(self, expense_data):
        """Identify potentially wasteful subscriptions"""

        # This is simplified - would need usage tracking
        subscriptions = []

        for expense in expense_data['items']:
            description = expense.get('name', '').lower()

            # Pattern match common subscriptions
            if any(keyword in description for keyword in ['subscription', 'monthly', 'saas']):
                subscriptions.append({
                    'name': expense['name'],
                    'amount': expense['amount_total'],
                    'vendor': expense['partner_id'][1] if expense.get('partner_id') else 'Unknown'
                })

        return subscriptions

    def generate_recommendations(self, analysis_results):
        """Generate proactive recommendations"""

        recommendations = []

        # Financial recommendations
        if analysis_results['financial']['monthly_progress']['status'] == 'behind':
            recommendations.append({
                'category': 'revenue',
                'priority': 'high',
                'recommendation': 'Revenue behind target. Consider: reaching out to past clients, promoting services on social media, or following up on pending proposals.'
            })

        # Bottleneck recommendations
        if len(analysis_results['bottlenecks']) > 0:
            recommendations.append({
                'category': 'operations',
                'priority': 'high',
                'recommendation': f'{len(analysis_results["bottlenecks"])} tasks stuck for >3 days. Review and unblock or delegate.'
            })

        # Subscription recommendations
        if len(analysis_results.get('subscriptions', [])) > 5:
            recommendations.append({
                'category': 'cost_optimization',
                'priority': 'medium',
                'recommendation': f'{len(analysis_results["subscriptions"])} active subscriptions detected. Review for unused services.'
            })

        return recommendations
```

### Component 3: Report Generator

```python
# watchers/ceo_briefing_generator.py
"""Generate CEO briefing report"""

from pathlib import Path
from datetime import datetime, timedelta
from data_collectors.financial_collector import FinancialDataCollector
from data_collectors.task_collector import TaskDataCollector
from data_collectors.communication_collector import CommunicationDataCollector
from analysis_engine import AnalysisEngine
import json

class CEOBriefingGenerator:
    def __init__(self, vault_path, odoo_client, business_goals):
        self.vault = Path(vault_path)
        self.briefings = self.vault / 'Briefings'
        self.briefings.mkdir(exist_ok=True)

        self.financial_collector = FinancialDataCollector(odoo_client, vault_path)
        self.task_collector = TaskDataCollector(vault_path)
        self.comm_collector = CommunicationDataCollector(vault_path)
        self.analyzer = AnalysisEngine(business_goals)

    def generate_weekly_briefing(self):
        """Generate weekly CEO briefing"""

        # Calculate date range (last 7 days)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)

        print(f"Generating CEO briefing for {start_date} to {end_date}")

        # Collect data
        financial_data = self.financial_collector.collect_weekly_data(start_date, end_date)
        task_data = self.task_collector.collect_weekly_data(start_date, end_date)
        comm_data = self.comm_collector.collect_weekly_data(start_date, end_date)

        # Analyze data
        financial_analysis = self.analyzer.analyze_financial_performance(financial_data)
        bottlenecks = self.analyzer.detect_bottlenecks(task_data)
        subscriptions = self.analyzer.detect_subscription_waste(financial_data['expenses'])

        analysis_results = {
            'financial': financial_analysis,
            'bottlenecks': bottlenecks,
            'subscriptions': subscriptions
        }

        recommendations = self.analyzer.generate_recommendations(analysis_results)

        # Generate report
        report = self._format_report(
            start_date, end_date,
            financial_data, task_data, comm_data,
            analysis_results, recommendations
        )

        # Save report
        filename = f"{end_date.strftime('%Y-%m-%d')}_Monday_Briefing.md"
        filepath = self.briefings / filename
        filepath.write_text(report)

        print(f"CEO briefing saved to {filepath}")
        return filepath

    def _format_report(self, start_date, end_date, financial, tasks, comm, analysis, recommendations):
        """Format the briefing report"""

        report = f"""# Weekly CEO Briefing

---
generated: {datetime.now().isoformat()}
period: {start_date} to {end_date}
---

## 📊 Executive Summary

{self._generate_executive_summary(analysis)}

## 💰 Financial Performance

### This Week
- **Revenue:** ${financial['revenue']['total']:,.2f} ({financial['revenue']['count']} invoices)
- **Expenses:** ${financial['expenses']['total']:,.2f} ({financial['expenses']['count']} items)
- **Net Income:** ${analysis['financial']['net']:,.2f}
- **Trend:** {analysis['financial']['trend'].upper()}

### Month-to-Date
- **Current:** ${analysis['financial']['monthly_progress']['current']:,.2f}
- **Target:** ${analysis['financial']['monthly_progress']['target']:,.2f}
- **Progress:** {analysis['financial']['monthly_progress']['percentage']:.1f}%
- **Status:** {analysis['financial']['monthly_progress']['status'].upper()}

### Accounts Receivable
- **Outstanding:** ${financial['receivables']['total_outstanding']:,.2f} ({financial['receivables']['count']} invoices)
- **Overdue:** ${financial['receivables']['overdue_amount']:,.2f} ({financial['receivables']['overdue_count']} invoices)

## ✅ Task Completion

### Completed This Week
- **Total:** {tasks['completed']['count']} tasks

{self._format_task_list(tasks['completed']['tasks'])}

### Pending Tasks
- **Total:** {tasks['pending']['count']} tasks
- **Urgent:** {len([t for t in tasks['pending']['tasks'] if t['priority'] == 'high'])} high priority

## 🚨 Bottlenecks Identified

{self._format_bottlenecks(analysis['bottlenecks'])}

## 📧 Communications

- **Emails Sent:** {comm['emails']['sent']}
- **Emails Received:** {comm['emails']['received']}
- **Social Media Posts:** {comm['social_media']['posts']}

## 💡 Proactive Recommendations

{self._format_recommendations(recommendations)}

## 📅 Upcoming This Week

{self._get_upcoming_deadlines()}

## 🎯 Action Items

{self._generate_action_items(analysis, recommendations)}

---

*Generated by AI Employee CEO Briefing System*
*Next briefing: {(end_date + timedelta(days=7)).strftime('%Y-%m-%d')}*
"""
        return report

    def _generate_executive_summary(self, analysis):
        """Generate 2-3 sentence executive summary"""

        financial_status = analysis['financial']['monthly_progress']['status']
        bottleneck_count = len(analysis['bottlenecks'])

        if financial_status == 'on_track' and bottleneck_count == 0:
            return "Strong week with revenue on track and no major bottlenecks. Operations running smoothly."
        elif financial_status == 'behind' and bottleneck_count > 0:
            return f"Revenue behind target and {bottleneck_count} bottlenecks identified. Immediate action required."
        elif financial_status == 'on_track' and bottleneck_count > 0:
            return f"Revenue on track but {bottleneck_count} operational bottlenecks need attention."
        else:
            return "Revenue behind target. Focus on sales and client outreach this week."

    def _format_task_list(self, tasks):
        """Format task list"""
        if not tasks:
            return "- No tasks completed this week"

        lines = []
        for task in tasks[:10]:  # Top 10
            lines.append(f"- [{task['type']}] {task['name']}")

        if len(tasks) > 10:
            lines.append(f"- ... and {len(tasks) - 10} more")

        return "\n".join(lines)

    def _format_bottlenecks(self, bottlenecks):
        """Format bottleneck section"""
        if not bottlenecks:
            return "No bottlenecks detected. All tasks progressing normally."

        lines = ["| Task | Age | Priority | Likely Cause |", "|------|-----|----------|--------------|"]
        for b in bottlenecks:
            lines.append(f"| {b['task']} | {b['age_days']} days | {b['priority']} | {b['likely_cause']} |")

        return "\n".join(lines)

    def _format_recommendations(self, recommendations):
        """Format recommendations"""
        if not recommendations:
            return "No specific recommendations at this time. Continue current operations."

        lines = []
        for i, rec in enumerate(recommendations, 1):
            priority_emoji = "🔴" if rec['priority'] == 'high' else "🟡"
            lines.append(f"{i}. {priority_emoji} **{rec['category'].replace('_', ' ').title()}:** {rec['recommendation']}")

        return "\n".join(lines)

    def _get_upcoming_deadlines(self):
        """Get upcoming deadlines from calendar/tasks"""
        # Simplified - would integrate with calendar
        return "- No upcoming deadlines in next 7 days"

    def _generate_action_items(self, analysis, recommendations):
        """Generate specific action items"""
        actions = []

        # High priority recommendations become action items
        for rec in recommendations:
            if rec['priority'] == 'high':
                actions.append(f"- [ ] {rec['recommendation']}")

        # Overdue invoices
        if analysis['financial'].get('receivables', {}).get('overdue_count', 0) > 0:
            actions.append("- [ ] Follow up on overdue invoices")

        # Bottlenecks
        if len(analysis['bottlenecks']) > 0:
            actions.append(f"- [ ] Review and unblock {len(analysis['bottlenecks'])} stuck tasks")

        if not actions:
            actions.append("- [ ] Review weekly performance and plan next week")

        return "\n".join(actions)


# CLI interface
if __name__ == '__main__':
    from odoo_client import OdooClient
    import os

    # Load configuration
    vault_path = os.getenv('VAULT_PATH', '/mnt/d/AI/Personal-AI-Employee/AI_Employee_Vault')

    odoo_client = OdooClient(
        os.getenv('ODOO_URL'),
        os.getenv('ODOO_DB'),
        os.getenv('ODOO_USERNAME'),
        os.getenv('ODOO_PASSWORD')
    )

    business_goals = {
        'monthly_revenue_target': 5000,
        'max_monthly_expenses': 1500
    }

    generator = CEOBriefingGenerator(vault_path, odoo_client, business_goals)
    generator.generate_weekly_briefing()
```

## Integration with Scheduler

Add to `scheduler.py`:

```python
# In scheduler.py
from ceo_briefing_generator import CEOBriefingGenerator

def generate_weekly_briefing():
    """Generate CEO briefing every Monday at 7 AM"""
    logger.info("Generating weekly CEO briefing")

    generator = CEOBriefingGenerator(
        vault_path=VAULT_PATH,
        odoo_client=odoo_client,
        business_goals=BUSINESS_GOALS
    )

    briefing_path = generator.generate_weekly_briefing()
    logger.info(f"CEO briefing generated: {briefing_path}")

    # Optional: Send notification
    # send_notification(f"Weekly CEO briefing ready: {briefing_path}")

# Schedule for Monday 7:00 AM
schedule.every().monday.at("07:00").do(generate_weekly_briefing)
```

## Example Output

```markdown
# Weekly CEO Briefing

---
generated: 2026-03-03T07:00:00Z
period: 2026-02-24 to 2026-03-02
---

## 📊 Executive Summary

Strong week with revenue on track and no major bottlenecks. Operations running smoothly.

## 💰 Financial Performance

### This Week
- **Revenue:** $2,450.00 (3 invoices)
- **Expenses:** $320.00 (8 items)
- **Net Income:** $2,130.00
- **Trend:** UP

### Month-to-Date
- **Current:** $4,500.00
- **Target:** $5,000.00
- **Progress:** 90.0%
- **Status:** ON_TRACK

### Accounts Receivable
- **Outstanding:** $1,200.00 (2 invoices)
- **Overdue:** $0.00 (0 invoices)

## ✅ Task Completion

### Completed This Week
- **Total:** 12 tasks

- [email] EMAIL_client_inquiry_response
- [invoice] INVOICE_client_a_february
- [social] LINKEDIN_POST_thought_leadership
- [email] EMAIL_vendor_payment_confirmation
- [task] TASK_budget_review_q1
- ... and 7 more

### Pending Tasks
- **Total:** 3 tasks
- **Urgent:** 1 high priority

## 🚨 Bottlenecks Identified

No bottlenecks detected. All tasks progressing normally.

## 📧 Communications

- **Emails Sent:** 8
- **Emails Received:** 15
- **Social Media Posts:** 4

## 💡 Proactive Recommendations

No specific recommendations at this time. Continue current operations.

## 📅 Upcoming This Week

- No upcoming deadlines in next 7 days

## 🎯 Action Items

- [ ] Review weekly performance and plan next week

---

*Generated by AI Employee CEO Briefing System*
*Next briefing: 2026-03-10*
```

## Testing

### Test 1: Generate Sample Briefing

```bash
# Set environment variables
export VAULT_PATH="/mnt/d/AI/Personal-AI-Employee/AI_Employee_Vault"
export ODOO_URL="http://localhost:8069"
export ODOO_DB="your_database"
export ODOO_USERNAME="admin"
export ODOO_PASSWORD="your_password"

# Generate briefing
python watchers/ceo_briefing_generator.py
```

### Test 2: Verify Data Collection

```python
# Test individual collectors
from data_collectors.task_collector import TaskDataCollector

collector = TaskDataCollector('/path/to/vault')
data = collector.collect_weekly_data(start_date, end_date)
print(json.dumps(data, indent=2))
```

## Customization

### Custom Metrics

Add custom metrics to analysis engine:

```python
def analyze_client_health(self, financial_data, comm_data):
    """Analyze client relationship health"""

    # Calculate response time
    # Track invoice payment speed
    # Monitor communication frequency

    return client_health_score
```

### Custom Recommendations

Add domain-specific recommendations:

```python
def generate_marketing_recommendations(self, social_data):
    """Generate marketing-specific recommendations"""

    if social_data['posts'] < 3:
        return "Social media activity below target (3-5 posts/week)"

    return None
```

## Monitoring

Track briefing generation:
- Generation time
- Data collection errors
- Analysis accuracy
- User engagement (do they read it?)

## Future Enhancements

1. **Trend Analysis:** Compare week-over-week, month-over-month
2. **Predictive Insights:** Forecast revenue based on pipeline
3. **Competitive Analysis:** Track industry benchmarks
4. **Visual Charts:** Generate ASCII charts or images
5. **Email Delivery:** Auto-send briefing via email
6. **Interactive Dashboard:** Web-based dashboard with drill-down

---

**Status:** Ready for implementation
**Dependencies:** Odoo MCP server, data collectors, analysis engine
**Next Steps:** Implement data collectors, test with sample data, integrate with scheduler
