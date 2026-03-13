#!/usr/bin/env python3
"""
Ralph Wiggum - Groq-Powered Autonomous Agent
Continuous iteration using Groq API instead of Claude Code
"""

import json
import os
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from groq import Groq

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GroqRalphWiggum:
    """Autonomous agent powered by Groq API with continuous iteration"""

    def __init__(self, vault_path: str, groq_api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.vault_path = Path(vault_path)
        self.groq_client = Groq(api_key=groq_api_key)
        self.model = model
        self.state_file = Path('/tmp/ralph_groq_state.json')
        self.log_file = Path('/tmp/ralph_groq.log')
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'

        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.done.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)

        # Conversation history
        self.messages = []

    def _get_system_prompt(self) -> str:
        """Get the system prompt for Ralph Wiggum mode"""
        return """You are Ralph Wiggum, an autonomous AI agent that works continuously until tasks are complete.

Your capabilities:
- Read and write files in the vault
- Execute bash commands
- Process tasks systematically
- Handle errors gracefully
- Continue working until completion criteria met

Your working directory: {vault_path}

Key folders:
- Needs_Action/: Tasks waiting to be processed
- Done/: Completed tasks
- Logs/: System logs
- Plans/: Planning documents
- Approvals/: Items needing human approval

When given a task, you will:
1. Assess what needs to be done
2. Work through each step systematically
3. Handle errors without stopping
4. Continue until completion criteria met
5. Log your progress

You respond with JSON commands to execute actions:
{{
  "thought": "Your reasoning about what to do next",
  "action": "read_file|write_file|bash|list_files|complete",
  "parameters": {{...}},
  "continue": true/false
}}

Available actions:
- read_file: {{"path": "relative/path/to/file"}}
- write_file: {{"path": "relative/path/to/file", "content": "file content"}}
- bash: {{"command": "bash command to execute"}}
- list_files: {{"directory": "relative/path"}}
- complete: {{"message": "completion message"}}

Set "continue": true if more work remains, false if task is complete.

Work systematically and thoroughly. Don't stop until the job is done!""".format(vault_path=self.vault_path)

    def _execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action and return the result"""
        try:
            if action == "read_file":
                path = self.vault_path / parameters["path"]
                if path.exists():
                    content = path.read_text()
                    return {"success": True, "content": content}
                else:
                    return {"success": False, "error": f"File not found: {path}"}

            elif action == "write_file":
                path = self.vault_path / parameters["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(parameters["content"])
                return {"success": True, "message": f"File written: {path}"}

            elif action == "bash":
                import subprocess
                result = subprocess.run(
                    parameters["command"],
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=str(self.vault_path),
                    timeout=60
                )
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }

            elif action == "list_files":
                directory = self.vault_path / parameters.get("directory", ".")
                if directory.exists() and directory.is_dir():
                    files = [str(f.relative_to(self.vault_path)) for f in directory.iterdir()]
                    return {"success": True, "files": files}
                else:
                    return {"success": False, "error": f"Directory not found: {directory}"}

            elif action == "complete":
                return {"success": True, "complete": True, "message": parameters.get("message", "Task complete")}

            else:
                return {"success": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            return {"success": False, "error": str(e)}

    def _check_completion(self, strategy: str, task_file: Optional[Path] = None) -> bool:
        """Check if task is complete based on strategy"""
        if strategy == "file_movement":
            if task_file:
                done_file = self.done / task_file.name
                return done_file.exists()
            return False

        elif strategy == "empty_folder":
            if not self.needs_action.exists():
                return True
            files = list(self.needs_action.iterdir())
            return len(files) == 0

        elif strategy == "promise":
            # Check last message for completion promise
            if self.messages:
                last_msg = self.messages[-1].get("content", "")
                return "<promise>TASK_COMPLETE</promise>" in last_msg
            return False

        return False

    def _call_groq(self, user_message: str) -> str:
        """Call Groq API and get response"""
        # Add user message
        self.messages.append({
            "role": "user",
            "content": user_message
        })

        # Call Groq API
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    *self.messages
                ],
                temperature=0.7,
                max_tokens=4096
            )

            assistant_message = response.choices[0].message.content

            # Add assistant response to history
            self.messages.append({
                "role": "assistant",
                "content": assistant_message
            })

            return assistant_message

        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            raise

    def run_loop(
        self,
        task_description: str,
        task_file: Optional[Path] = None,
        completion_strategy: str = "empty_folder",
        max_iterations: int = 10,
        max_time_minutes: int = 30
    ):
        """Run the autonomous loop until task is complete"""

        logger.info(f"🚀 Starting Ralph Wiggum (Groq-powered)")
        logger.info(f"Task: {task_description}")
        logger.info(f"Strategy: {completion_strategy}")
        logger.info(f"Max iterations: {max_iterations}")
        logger.info(f"Max time: {max_time_minutes} minutes")

        # Create state file
        state = {
            "task_name": task_description,
            "task_file": str(task_file) if task_file else None,
            "completion_strategy": completion_strategy,
            "iteration": 0,
            "start_time": int(time.time()),
            "max_iterations": max_iterations,
            "max_time_minutes": max_time_minutes
        }
        self.state_file.write_text(json.dumps(state, indent=2))

        start_time = time.time()
        iteration = 0

        # Initial prompt
        current_prompt = task_description

        while iteration < max_iterations:
            iteration += 1
            elapsed_minutes = (time.time() - start_time) / 60

            logger.info(f"\n{'='*60}")
            logger.info(f"Iteration {iteration}/{max_iterations} (Time: {elapsed_minutes:.1f}m)")
            logger.info(f"{'='*60}")

            # Update state
            state["iteration"] = iteration
            self.state_file.write_text(json.dumps(state, indent=2))

            # Check time limit
            if elapsed_minutes > max_time_minutes:
                logger.warning(f"⏰ Time limit reached ({max_time_minutes} minutes)")
                break

            # Call Groq
            logger.info(f"📤 Sending to Groq: {current_prompt[:100]}...")
            response = self._call_groq(current_prompt)
            logger.info(f"📥 Received response ({len(response)} chars)")

            # Try to parse JSON response
            try:
                # Extract JSON from response (might be wrapped in markdown)
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    action_data = json.loads(json_str)

                    logger.info(f"💭 Thought: {action_data.get('thought', 'N/A')}")
                    logger.info(f"🎬 Action: {action_data.get('action', 'N/A')}")

                    # Execute action
                    action = action_data.get("action")
                    parameters = action_data.get("parameters", {})

                    if action and action != "complete":
                        result = self._execute_action(action, parameters)
                        logger.info(f"✅ Result: {result.get('success', False)}")

                        # Prepare next prompt with result
                        current_prompt = f"Action result: {json.dumps(result)}\n\nContinue with the task."

                    # Check if agent says it's done
                    if not action_data.get("continue", True) or action == "complete":
                        logger.info("🎯 Agent signaled completion")
                        break

                else:
                    # No JSON found, treat as text response
                    logger.info(f"📝 Text response: {response[:200]}...")
                    current_prompt = "Continue with the task. Remember to respond with JSON commands."

            except json.JSONDecodeError:
                logger.warning("⚠️ Could not parse JSON response, continuing...")
                current_prompt = "Please respond with valid JSON commands to continue the task."

            # Check completion criteria
            if self._check_completion(completion_strategy, task_file):
                logger.info("✅ Completion criteria met!")
                break

            # Small delay between iterations
            time.sleep(1)

        # Final status
        elapsed_time = time.time() - start_time
        logger.info(f"\n{'='*60}")
        logger.info(f"🏁 Ralph Wiggum Loop Complete")
        logger.info(f"{'='*60}")
        logger.info(f"Iterations: {iteration}/{max_iterations}")
        logger.info(f"Time: {elapsed_time/60:.1f} minutes")
        logger.info(f"Completion: {self._check_completion(completion_strategy, task_file)}")

        # Save final log
        log_data = {
            "task": task_description,
            "strategy": completion_strategy,
            "iterations": iteration,
            "time_seconds": elapsed_time,
            "completed": self._check_completion(completion_strategy, task_file),
            "timestamp": datetime.now().isoformat()
        }

        log_file = self.logs / f"ralph_groq_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_file.write_text(json.dumps(log_data, indent=2))

        # Clean up state file if complete
        if self._check_completion(completion_strategy, task_file):
            if self.state_file.exists():
                self.state_file.unlink()
            logger.info("✅ Task completed successfully!")
        else:
            logger.warning("⚠️ Task may be incomplete - review logs")

        return log_data


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Ralph Wiggum - Groq-Powered Autonomous Agent'
    )
    parser.add_argument('task', help='Task description')
    parser.add_argument(
        '--vault',
        default='/mnt/d/AI/Personal-AI-Employee/AI_Employee_Vault',
        help='Path to vault directory'
    )
    parser.add_argument(
        '--strategy',
        default='empty_folder',
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
    parser.add_argument(
        '--model',
        default='llama-3.3-70b-versatile',
        help='Groq model to use'
    )

    args = parser.parse_args()

    # Get Groq API key from environment
    groq_api_key = os.getenv('GROQ_API_KEY')
    if not groq_api_key:
        logger.error("GROQ_API_KEY environment variable not set")
        logger.error("Get your free API key at: https://console.groq.com")
        return 1

    # Validate vault path
    vault_path = Path(args.vault)
    if not vault_path.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        return 1

    # Create orchestrator
    ralph = GroqRalphWiggum(
        vault_path=str(vault_path),
        groq_api_key=groq_api_key,
        model=args.model
    )

    # Parse task file if provided
    task_file = Path(args.task_file) if args.task_file else None

    # Run loop
    try:
        result = ralph.run_loop(
            task_description=args.task,
            task_file=task_file,
            completion_strategy=args.strategy,
            max_iterations=args.max_iterations,
            max_time_minutes=args.max_time
        )

        if result["completed"]:
            logger.info("🎉 Success!")
            return 0
        else:
            logger.warning("⚠️ Task incomplete")
            return 1

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Failed: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
