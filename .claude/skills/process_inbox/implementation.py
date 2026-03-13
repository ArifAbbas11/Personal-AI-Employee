#!/usr/bin/env python3
"""
Process Inbox Files - Agent Skill Implementation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "watchers"))

from filesystem_watcher import FilesystemWatcher

def process_inbox(vault_path: str = "AI_Employee_Vault"):
    """Process all files in Inbox folder"""
    
    watcher = FilesystemWatcher(vault_path)
    
    # Check for new files
    new_files = watcher.check_for_updates()
    
    if not new_files:
        print("📭 No new files in Inbox")
        return []
    
    print(f"📬 Found {len(new_files)} new file(s) in Inbox")
    
    action_files = []
    for file_path in new_files:
        action_file = watcher.create_action_file(file_path)
        print(f"✅ Created action item: {action_file.name}")
        action_files.append(action_file)
    
    print(f"\n✨ Processed {len(new_files)} file(s)")
    print(f"📁 Action items created in: {watcher.needs_action}")
    
    return action_files

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--vault', default='AI_Employee_Vault')
    args = parser.parse_args()
    
    process_inbox(args.vault)
