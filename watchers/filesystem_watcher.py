#!/usr/bin/env python3
"""
Filesystem Watcher
Monitors a drop folder for new files and creates action items
"""

import sys
from pathlib import Path
from datetime import datetime
import shutil

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher

class FilesystemWatcher(BaseWatcher):
    """Watches a drop folder for new files"""
    
    def __init__(self, vault_path: str, drop_folder: str = None):
        super().__init__(vault_path, check_interval=10)
        
        # Set up drop folder
        if drop_folder:
            self.drop_folder = Path(drop_folder)
        else:
            self.drop_folder = self.vault_path / 'Inbox'
        
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        self.processed_files = set()
        
        self.logger.info(f'Watching drop folder: {self.drop_folder}')
    
    def check_for_updates(self) -> list:
        """Check for new files in drop folder"""
        new_files = []
        
        # Get all files in drop folder
        for file_path in self.drop_folder.iterdir():
            if file_path.is_file() and file_path.name not in self.processed_files:
                # Skip hidden files and .md files (those are metadata)
                if not file_path.name.startswith('.') and not file_path.name.endswith('.md'):
                    new_files.append(file_path)
        
        return new_files
    
    def create_action_file(self, file_path: Path) -> Path:
        """Create action file for dropped file"""
        
        # Get file info
        file_size = file_path.stat().st_size
        file_ext = file_path.suffix
        
        # Determine file type and suggested actions
        if file_ext in ['.csv', '.xlsx', '.xls']:
            file_type = 'spreadsheet'
            suggested_actions = [
                '[ ] Review data',
                '[ ] Import to accounting system',
                '[ ] Generate summary report'
            ]
        elif file_ext in ['.pdf', '.doc', '.docx']:
            file_type = 'document'
            suggested_actions = [
                '[ ] Review document',
                '[ ] Extract key information',
                '[ ] File appropriately'
            ]
        elif file_ext in ['.jpg', '.png', '.gif']:
            file_type = 'image'
            suggested_actions = [
                '[ ] Review image',
                '[ ] Add to media library',
                '[ ] Process if needed'
            ]
        else:
            file_type = 'file'
            suggested_actions = [
                '[ ] Review file',
                '[ ] Determine appropriate action'
            ]
        
        # Create metadata content
        content = self.create_metadata_header(
            'file_drop',
            original_name=file_path.name,
            file_type=file_type,
            size_bytes=file_size,
            extension=file_ext,
            priority='medium'
        )
        
        content += f"""## New File Dropped

**File:** {file_path.name}
**Type:** {file_type}
**Size:** {self._format_size(file_size)}
**Location:** {file_path}

## Suggested Actions

{chr(10).join(suggested_actions)}

## Notes

Add any relevant notes or context here.
"""
        
        # Create action file
        action_filename = f'FILE_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{file_path.stem}.md'
        action_path = self.needs_action / action_filename
        action_path.write_text(content)
        
        # Mark as processed
        self.processed_files.add(file_path.name)
        
        return action_path
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Filesystem Watcher')
    parser.add_argument('--vault', default='AI_Employee_Vault', help='Path to Obsidian vault')
    parser.add_argument('--drop-folder', help='Path to drop folder (default: vault/Inbox)')
    
    args = parser.parse_args()
    
    watcher = FilesystemWatcher(args.vault, args.drop_folder)
    
    try:
        watcher.run()
    except KeyboardInterrupt:
        print('\nWatcher stopped by user')
