#!/usr/bin/env python3
"""
Ralph Wiggum Orchestrator
Manages autonomous task loops with Claude Code
"""

import json
import subprocess
import time
import os
from pathlib import Path
from datetime import datetime
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RalphWiggumOrchestrator:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.state_file = Path('/tmp/ralph_wiggum_state.json')
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'

    def start_loop(
        self,
        task_description: str,
        task_file: Path = None,
        completion_strategy: str = 'file_movement',
        max_iterations: int = 10,
        max_time_minutes: int = 30
    ):
        """
        Start a Ralph Wiggum autonomous loop

        Args:
            task_description: Natural language description of task
            task_file: Optional specific file to process
            completion_strategy: 'file_movement', 'promise', or 'empty_folder'
            max_iterations: Maximum loop iterations
            max_time_minutes: Maximum time in minutes
        """
        logger.info(f"Starting Ralph Wiggum loop: {task_description}")

        # Create state file
        state = {
            'task_name': task_description,
            'task_file': str(task_file) if task_file else None,
            'completion_strategy': completion_strategy,
            'iteration': 1,
            'start_time': int(time.time()),
            'max_iterations': max_iterations,
            'max_time_minutes': max_time_minutes
        }

        self.state_file.write_text(json.dumps(state, indent=2))
        logger.info(f"State file created: {self.state_file}")

        # Set environment variables for stop hook
        env = os.environ.copy()
        env.update({
            'VAULT_PATH': str(self.vault_path),
            'STATE_FILE': str(self.state_file),
            'MAX_ITERATIONS': str(max_iterations),
            'MAX_TIME_MINUTES': str(max_time_minutes)
        })

        # Build Claude Code command
        claude_prompt = self._build_prompt(task_description, task_file)

        logger.info("Starting Claude Code with Ralph Wiggum mode")
        logger.info(f"Completion strategy: {completion_strategy}")
        logger.info(f"Max iterations: {max_iterations}")
        logger.info(f"Max time: {max_time_minutes} minutes")

        # Execute Claude Code with Ralph Wiggum mode
        try:
            # Note: This is a simplified version
            # In production, you'd integrate with Claude Code's actual execution
            result = subprocess.run(
                ['claude', claude_prompt],
                env=env,
                capture_output=True,
                text=True,
                timeout=max_time_minutes * 60,
                cwd=str(self.vault_path)
            )

            logger.info(f"Ralph Wiggum loop completed")
            logger.info(f"Exit code: {result.returncode}")

            # Check if task completed successfully
            if self.state_file.exists():
                logger.warning("State file still exists - task may be incomplete")
                state = json.loads(self.state_file.read_text())
                logger.warning(f"Final iteration: {state['iteration']}")
                logger.warning(f"You may need to review the task manually")
            else:
                logger.info("✅ Task completed successfully!")

            return result

        except subprocess.TimeoutExpired:
            logger.error(f"Ralph Wiggum loop timed out after {max_time_minutes} minutes")
            if self.state_file.exists():
                self.state_file.unlink()
            raise
        except FileNotFoundError:
            logger.error("Claude Code not found. Make sure 'claude' command is in PATH")
            logger.error("You may need to run this manually with: claude '<prompt>'")
            if self.state_file.exists():
                self.state_file.unlink()
            raise
        except Exception as e:
            logger.error(f"Error during Ralph Wiggum loop: {e}")
            if self.state_file.exists():
                self.state_file.unlink()
            raise

    def _build_prompt(self, task_description: str, task_file: Path = None) -> str:
        """Build the initial prompt for Claude"""
        prompt = f"""You are in Ralph Wiggum autonomous mode. Work on this task until it is COMPLETELY finished:

{task_description}

IMPORTANT INSTRUCTIONS:
1. Work through ALL steps required to complete this task
2. Do not stop until the task is fully complete
3. If you encounter errors, handle them and continue
4. Move completed task files to /Done when finished
5. Update the Dashboard with your progress

The stop hook will check if you're done and re-prompt you if not.
Keep working until the task is truly complete!
"""

        if task_file:
            prompt += f"\n\nTask file: {task_file}"

        return prompt

    def stop_loop(self):
        """Emergency stop - terminates the loop"""
        if self.state_file.exists():
            self.state_file.unlink()
            logger.info("Ralph Wiggum loop stopped manually")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Ralph Wiggum Autonomous Loop - Keep Claude working until task complete'
    )
    parser.add_argument('task', help='Task description')
    parser.add_argument(
        '--vault',
        default='/mnt/d/AI/Personal-AI-Employee/AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--strategy',
        default='file_movement',
        choices=['file_movement', 'promise', 'empty_folder'],
        help='Completion detection strategy'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=10,
        help='Maximum iterations'
    )
    parser.add_argument(
        '--max-time',
        type=int,
        default=30,
        help='Maximum time in minutes'
    )
    parser.add_argument(
        '--task-file',
        help='Specific task file to process'
    )

    args = parser.parse_args()

    # Validate vault path
    vault_path = Path(args.vault)
    if not vault_path.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        sys.exit(1)

    # Create orchestrator
    orchestrator = RalphWiggumOrchestrator(args.vault)

    # Parse task file if provided
    task_file = Path(args.task_file) if args.task_file else None

    # Start loop
    try:
        orchestrator.start_loop(
            task_description=args.task,
            task_file=task_file,
            completion_strategy=args.strategy,
            max_iterations=args.max_iterations,
            max_time_minutes=args.max_time
        )
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        orchestrator.stop_loop()
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to complete task: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
