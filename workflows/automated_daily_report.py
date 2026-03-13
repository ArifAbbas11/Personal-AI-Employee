#!/usr/bin/env python3
"""
Production Automation: Automated Daily Report
Generates comprehensive daily business report
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent.parent / "watchers"))

from automation.resource_manager import ResourceManager
from multi_agent.base import AgentCoordinator
from learning.feedback_loop import FeedbackLoopSystem


def generate_daily_report() -> Dict:
    """Generate comprehensive daily business report"""
    
    print(f"\n{'='*80}")
    print(f"AUTOMATED DAILY REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'sections': {}
    }
    
    # Section 1: System Health
    print("📊 SYSTEM HEALTH")
    print("-" * 80)
    
    resources = ResourceManager('AI_Employee_Vault')
    status = resources.monitor_resources()
    
    system_health = {
        'cpu_utilization': status['cpu']['utilization'],
        'memory_utilization': status['memory']['utilization'],
        'disk_utilization': status['disk']['utilization'],
        'status': 'healthy' if all([
            status['cpu']['utilization'] < 80,
            status['memory']['utilization'] < 80,
            status['disk']['utilization'] < 85
        ]) else 'warning'
    }
    
    report['sections']['system_health'] = system_health
    
    print(f"  CPU:    {system_health['cpu_utilization']:>5.1f}% {'✅' if system_health['cpu_utilization'] < 80 else '⚠️'}")
    print(f"  Memory: {system_health['memory_utilization']:>5.1f}% {'✅' if system_health['memory_utilization'] < 80 else '⚠️'}")
    print(f"  Disk:   {system_health['disk_utilization']:>5.1f}% {'✅' if system_health['disk_utilization'] < 85 else '⚠️'}")
    print(f"  Overall: {system_health['status'].upper()}")
    
    # Section 2: Agent Activity
    print(f"\n🤖 AGENT ACTIVITY")
    print("-" * 80)
    
    coordinator = AgentCoordinator('AI_Employee_Vault')
    agent_status = coordinator.get_system_status()
    
    agent_activity = {
        'total_agents': agent_status['total_agents'],
        'active_agents': agent_status['active_agents'],
        'tasks_completed': agent_status['completed_tasks'],
        'tasks_pending': agent_status['pending_tasks']
    }
    
    report['sections']['agent_activity'] = agent_activity
    
    print(f"  Total Agents: {agent_activity['total_agents']}")
    print(f"  Active Agents: {agent_activity['active_agents']}")
    print(f"  Tasks Completed: {agent_activity['tasks_completed']}")
    print(f"  Tasks Pending: {agent_activity['tasks_pending']}")
    
    # Section 3: Learning Progress
    print(f"\n🧠 LEARNING PROGRESS")
    print("-" * 80)
    
    feedback = FeedbackLoopSystem('AI_Employee_Vault')
    
    # Get stats for key models
    models = ['expense_categorizer', 'task_predictor', 'content_optimizer']
    learning_progress = {}
    
    for model in models:
        stats = feedback.get_model_statistics(model)
        learning_progress[model] = {
            'total_feedback': stats.get('total_feedback', 0),
            'accuracy': stats.get('accuracy', 0.0)
        }
        print(f"  {model}:")
        print(f"    Feedback Items: {stats.get('total_feedback', 0)}")
        print(f"    Accuracy: {stats.get('accuracy', 0.0):.1%}")
    
    report['sections']['learning_progress'] = learning_progress
    
    # Section 4: Recent Activity
    print(f"\n📁 RECENT ACTIVITY")
    print("-" * 80)
    
    vault_path = Path(__file__).parent.parent / "AI_Employee_Vault"
    
    # Count files in key directories
    done_files = list((vault_path / "Done").glob("*"))
    recent_done = [f for f in done_files if (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)) < timedelta(days=1)]
    
    needs_action = list((vault_path / "Needs_Action").glob("*"))
    inbox = list((vault_path / "Inbox").glob("*"))
    
    recent_activity = {
        'completed_today': len(recent_done),
        'needs_action': len(needs_action),
        'inbox': len(inbox)
    }
    
    report['sections']['recent_activity'] = recent_activity
    
    print(f"  Completed Today: {len(recent_done)}")
    print(f"  Needs Action: {len(needs_action)}")
    print(f"  In Inbox: {len(inbox)}")
    
    # Section 5: Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("-" * 80)
    
    recommendations = []
    
    if system_health['cpu_utilization'] > 70:
        recommendations.append("Consider scaling resources - CPU usage is high")
    
    if agent_activity['tasks_pending'] > 10:
        recommendations.append(f"{agent_activity['tasks_pending']} tasks pending - review task queue")
    
    if len(inbox) > 0:
        recommendations.append(f"{len(inbox)} items in inbox - process pending tasks")
    
    if len(needs_action) > 0:
        recommendations.append(f"{len(needs_action)} items need action - review and prioritize")
    
    if not recommendations:
        recommendations.append("All systems operating normally - no action required")
    
    report['sections']['recommendations'] = recommendations
    
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    # Save report
    report_file = f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
    report_path = vault_path / "Done" / report_file
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"✅ Report saved to: {report_path}")
    print(f"{'='*80}\n")
    
    return report


if __name__ == "__main__":
    generate_daily_report()
