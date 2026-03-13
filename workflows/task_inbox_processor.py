#!/usr/bin/env python3
"""
Production Workflow: Task Inbox Processing
Automatically routes tasks from inbox to appropriate handlers
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent / "watchers"))

from automation.task_router import TaskRouter


def process_task_inbox(inbox_file: str = None) -> Dict:
    """Process tasks from inbox file or directory"""
    
    router = TaskRouter("AI_Employee_Vault")
    
    # Get tasks from inbox
    inbox_path = Path(__file__).parent.parent / "AI_Employee_Vault" / "Inbox"
    
    if inbox_file:
        task_files = [Path(inbox_file)]
    else:
        task_files = list(inbox_path.glob("*.json"))
    
    if not task_files:
        print("📭 No tasks in inbox")
        return {'processed': 0, 'tasks': []}
    
    print(f"\n{'='*80}")
    print(f"TASK INBOX PROCESSING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    print(f"\nProcessing {len(task_files)} tasks from inbox\n")
    
    results = []
    routing_stats = {}
    
    for i, task_file in enumerate(task_files, 1):
        try:
            with open(task_file, 'r') as f:
                task_data = json.load(f)
            
            # Route the task
            result = router.route_task({
                'description': task_data.get('description', ''),
                'priority': task_data.get('priority', 'medium'),
                'category': task_data.get('category', 'general')
            })
            
            destination = result['destination']
            confidence = result['confidence']
            
            # Track routing stats
            routing_stats[destination] = routing_stats.get(destination, 0) + 1
            
            # Store result
            task_result = {
                'task_id': task_data.get('id', f'task_{i}'),
                'description': task_data.get('description', ''),
                'priority': task_data.get('priority', 'medium'),
                'destination': destination,
                'confidence': confidence,
                'routed_at': datetime.now().isoformat()
            }
            results.append(task_result)
            
            # Print progress
            priority_icon = '🔴' if task_data.get('priority') == 'high' else '🟡' if task_data.get('priority') == 'medium' else '🟢'
            print(f"{i:3d}. {priority_icon} {task_data.get('description', '')[:60]}")
            print(f"     → {destination} ({confidence:.1%})")
            
            # Move processed task to Done
            done_path = Path(__file__).parent.parent / "AI_Employee_Vault" / "Done" / task_file.name
            task_file.rename(done_path)
            
        except Exception as e:
            print(f"⚠️  Error processing {task_file.name}: {e}")
            continue
    
    # Generate summary
    print(f"\n{'='*80}")
    print("ROUTING SUMMARY")
    print(f"{'='*80}")
    print(f"\nTotal Tasks Processed: {len(results)}\n")
    
    print("By Destination:")
    for destination, count in sorted(routing_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(results)) * 100
        print(f"  {destination:30s}: {count:3d} tasks ({percentage:>5.1f}%)")
    
    # Save routing report
    report_file = f"routing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path = Path(__file__).parent.parent / "AI_Employee_Vault" / "Done" / report_file
    
    report = {
        'processed_at': datetime.now().isoformat(),
        'total_tasks': len(results),
        'routing_stats': routing_stats,
        'tasks': results
    }
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Report saved to: {report_path}")
    print(f"{'='*80}\n")
    
    return report


if __name__ == "__main__":
    inbox_file = sys.argv[1] if len(sys.argv) > 1 else None
    process_task_inbox(inbox_file)
