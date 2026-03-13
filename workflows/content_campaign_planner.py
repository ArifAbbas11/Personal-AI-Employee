#!/usr/bin/env python3
"""
Production Workflow: Content Campaign Planning
Plans and optimizes content across multiple platforms
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent / "watchers"))

from multi_agent.base import AgentCoordinator, TaskPriority
from multi_agent.marketing_agent import MarketingAgent


def plan_content_campaign(campaign_file: str) -> Dict:
    """Plan content campaign from JSON file"""
    
    coordinator = AgentCoordinator("AI_Employee_Vault")
    marketing = MarketingAgent("AI_Employee_Vault", coordinator)
    
    # Load campaign data
    with open(campaign_file, 'r') as f:
        campaign = json.load(f)
    
    content_items = campaign.get('content_items', [])
    
    if not content_items:
        return {'error': 'No content items found'}
    
    print(f"\n{'='*80}")
    print(f"CONTENT CAMPAIGN PLANNING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    print(f"\nCampaign: {campaign.get('name', 'Untitled')}")
    print(f"Planning {len(content_items)} content pieces\n")
    
    results = []
    platform_stats = {}
    total_predicted_engagement = 0
    
    for i, item in enumerate(content_items, 1):
        # Optimize content
        task = coordinator.delegate_task(
            task_type="optimize_content",
            description=f"Optimize: {item['title']}",
            priority=TaskPriority.MEDIUM,
            metadata={
                'title': item['title'],
                'content': item.get('content', f"Content about {item['title']}"),
                'platform': item['platform']
            }
        )
        
        result = marketing.process_task(task)
        
        platform = item['platform']
        engagement = result['predicted_engagement']
        
        # Track stats
        platform_stats[platform] = platform_stats.get(platform, {'count': 0, 'total_engagement': 0})
        platform_stats[platform]['count'] += 1
        platform_stats[platform]['total_engagement'] += engagement
        total_predicted_engagement += engagement
        
        # Store result
        content_result = {
            **item,
            'predicted_engagement': engagement,
            'recommendations': result['recommendations'],
            'optimized_at': datetime.now().isoformat()
        }
        results.append(content_result)
        
        # Print progress
        emoji = '📱' if platform == 'twitter' else '💼' if platform == 'linkedin' else '📸' if platform == 'instagram' else '📘'
        print(f"{i:3d}. {emoji} {item['title'][:55]}")
        print(f"     Platform: {platform}")
        print(f"     Engagement: {engagement:.1f}/10")
        print(f"     Top Tip: {result['recommendations'][0][:70]}")
        print()
    
    # Generate summary
    print(f"{'='*80}")
    print("CAMPAIGN SUMMARY")
    print(f"{'='*80}")
    print(f"\nTotal Content Pieces: {len(results)}")
    print(f"Average Predicted Engagement: {total_predicted_engagement/len(results):.1f}/10\n")
    
    print("By Platform:")
    for platform, stats in sorted(platform_stats.items(), key=lambda x: x[1]['count'], reverse=True):
        avg_engagement = stats['total_engagement'] / stats['count']
        print(f"  {platform:15s}: {stats['count']:2d} pieces (avg engagement: {avg_engagement:.1f}/10)")
    
    # Identify high/low performers
    high_performers = [r for r in results if r['predicted_engagement'] >= 6.0]
    low_performers = [r for r in results if r['predicted_engagement'] < 4.0]
    
    if high_performers:
        print(f"\n✅ High Performers ({len(high_performers)}):")
        for item in high_performers[:3]:
            print(f"  • {item['title']} ({item['platform']}) - {item['predicted_engagement']:.1f}/10")
    
    if low_performers:
        print(f"\n⚠️  Needs Improvement ({len(low_performers)}):")
        for item in low_performers[:3]:
            print(f"  • {item['title']} ({item['platform']}) - {item['predicted_engagement']:.1f}/10")
    
    # Save campaign plan
    output_file = f"campaign_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_path = Path(__file__).parent.parent / "AI_Employee_Vault" / "Plans" / output_file
    
    plan = {
        'campaign_name': campaign.get('name', 'Untitled'),
        'planned_at': datetime.now().isoformat(),
        'total_content': len(results),
        'average_engagement': total_predicted_engagement / len(results),
        'platform_stats': platform_stats,
        'content_items': results
    }
    
    with open(output_path, 'w') as f:
        json.dump(plan, f, indent=2)
    
    print(f"\n✅ Campaign plan saved to: {output_path}")
    print(f"{'='*80}\n")
    
    return plan


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python content_campaign_planner.py <campaign.json>")
        print("\nJSON format:")
        print('{')
        print('  "name": "Q2 Product Launch",')
        print('  "content_items": [')
        print('    {"title": "Announcing New Features", "platform": "linkedin"},')
        print('    {"title": "Behind the Scenes", "platform": "instagram"}')
        print('  ]')
        print('}')
        sys.exit(1)
    
    campaign_file = sys.argv[1]
    
    if not Path(campaign_file).exists():
        print(f"❌ Error: File not found: {campaign_file}")
        sys.exit(1)
    
    plan_content_campaign(campaign_file)
