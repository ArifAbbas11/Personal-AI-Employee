#!/usr/bin/env python3
"""
Generate CEO Briefing - Agent Skill Implementation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "workflows"))

from ceo_briefing_generator import CEOBriefingGenerator

def generate_ceo_briefing(vault_path: str = "AI_Employee_Vault", days: int = 7):
    """Generate CEO briefing for specified period"""
    
    generator = CEOBriefingGenerator(vault_path)
    briefing_path = generator.generate_briefing(days)
    
    print(f"\n✅ CEO Briefing generated successfully!")
    print(f"📊 Location: {briefing_path}")
    print(f"\n💡 Open in Obsidian to review your business insights")
    
    return briefing_path

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=7)
    parser.add_argument('--vault', default='AI_Employee_Vault')
    args = parser.parse_args()
    
    generate_ceo_briefing(args.vault, args.days)
