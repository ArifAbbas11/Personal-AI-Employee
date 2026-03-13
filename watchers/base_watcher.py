"""
Base Watcher Class
Template for all watcher implementations
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BaseWatcher(ABC):
    """Base class for all watchers"""
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
    @abstractmethod
    def check_for_updates(self) -> list:
        """Return list of new items to process"""
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        """Create .md file in Needs_Action folder"""
        pass
    
    def run(self):
        """Main loop - runs continuously"""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval} seconds')
        
        while True:
            try:
                items = self.check_for_updates()
                if items:
                    self.logger.info(f'Found {len(items)} new items')
                    for item in items:
                        filepath = self.create_action_file(item)
                        self.logger.info(f'Created action file: {filepath.name}')
                else:
                    self.logger.debug('No new items found')
                    
            except Exception as e:
                self.logger.error(f'Error in main loop: {e}', exc_info=True)
                
            time.sleep(self.check_interval)
    
    def create_metadata_header(self, item_type: str, **kwargs) -> str:
        """Create YAML frontmatter for action files"""
        header = f"""---
type: {item_type}
created: {datetime.now().isoformat()}
status: pending
"""
        for key, value in kwargs.items():
            header += f"{key}: {value}\n"
        header += "---\n\n"
        return header
