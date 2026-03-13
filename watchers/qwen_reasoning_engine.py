#!/usr/bin/env python3
"""
Qwen Reasoning Engine - The Brain of AI Employee
Reads from Needs_Action, generates Plans, creates approval requests
"""

import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QwenReasoningEngine:
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action_dir = self.vault_path / 'Needs_Action'
        self.plans_dir = self.vault_path / 'Plans'
        self.pending_approval_dir = self.vault_path / 'Pending_Approval'
        self.done_dir = self.vault_path / 'Done'
        self.check_interval = check_interval

        # LLM Backend Configuration (Hybrid: Ollama or Groq)
        self.llm_backend = os.getenv('LLM_BACKEND', 'ollama').lower()

        if self.llm_backend == 'ollama':
            # Local Ollama setup
            ollama_host = os.getenv('OLLAMA_HOST', 'localhost')
            self.ollama_url = f"http://{ollama_host}:11434/api/generate"
            self.model = "qwen2.5-coder:7b"
        elif self.llm_backend == 'groq':
            # Cloud Groq setup (free)
            self.groq_api_key = os.getenv('GROQ_API_KEY')
            self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
            self.model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')  # Free, fast, smart
            if not self.groq_api_key:
                logger.error("❌ GROQ_API_KEY not set! Get free key at: https://console.groq.com")
        else:
            logger.error(f"❌ Unknown LLM_BACKEND: {self.llm_backend}")
            self.llm_backend = 'ollama'  # Fallback

        # Create directories if they don't exist
        self.plans_dir.mkdir(parents=True, exist_ok=True)
        self.pending_approval_dir.mkdir(parents=True, exist_ok=True)

        # Load company handbook for context
        self.handbook = self._load_handbook()

        logger.info("✅ Qwen Reasoning Engine initialized")
        logger.info(f"   Backend: {self.llm_backend.upper()}")
        logger.info(f"   Model: {self.model}")
        logger.info(f"   Vault: {self.vault_path}")

    def _load_handbook(self) -> str:
        """Load company handbook for context"""
        handbook_path = self.vault_path / 'Company_Handbook.md'
        if handbook_path.exists():
            return handbook_path.read_text()
        return "No company handbook found. Use general best practices."

    def query_ollama(self, prompt: str, system_prompt: str = None) -> str:
        """Query Ollama API (local)"""
        try:
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            }

            response = requests.post(self.ollama_url, json=payload, timeout=120)
            response.raise_for_status()

            result = response.json()
            return result.get('response', '').strip()

        except Exception as e:
            logger.error(f"Error querying Ollama: {e}")
            return ""

    def query_groq(self, prompt: str, system_prompt: str = None) -> str:
        """Query Groq API (cloud, free)"""
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 0.9
            }

            response = requests.post(self.groq_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            return result['choices'][0]['message']['content'].strip()

        except Exception as e:
            logger.error(f"Error querying Groq: {e}")
            return ""

    def query_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Query LLM - supports both Ollama (local) and Groq (cloud)"""
        if self.llm_backend == 'groq':
            return self.query_groq(prompt, system_prompt)
        else:
            return self.query_ollama(prompt, system_prompt)

    def analyze_task(self, task_file: Path) -> dict:
        """Analyze a task file and generate reasoning"""
        try:
            content = task_file.read_text()

            system_prompt = f"""You are an AI Employee assistant. Your role is to analyze tasks and create actionable plans.

Company Handbook:
{self.handbook}

Guidelines:
1. Be concise and actionable
2. Identify if human approval is needed for sensitive actions (payments, emails to new contacts, etc.)
3. Break down complex tasks into steps
4. Consider security and privacy
5. Flag any risks or concerns"""

            user_prompt = f"""Analyze this task and provide:
1. Task Type (email, social_media, payment, general)
2. Priority (high, medium, low)
3. Requires Approval (yes/no) - yes for: payments, emails to new contacts, social posts, sensitive data
4. Suggested Actions (numbered list)
5. Risks/Concerns (if any)

Task File: {task_file.name}
Content:
{content}

Provide your analysis in this exact format:
TASK_TYPE: [type]
PRIORITY: [priority]
REQUIRES_APPROVAL: [yes/no]
ACTIONS:
1. [action 1]
2. [action 2]
...
RISKS: [any concerns or "None"]
"""

            response = self.query_llm(user_prompt, system_prompt)

            # Parse response
            analysis = {
                'task_type': 'general',
                'priority': 'medium',
                'requires_approval': True,  # Default to safe
                'actions': [],
                'risks': 'None'
            }

            for line in response.split('\n'):
                line = line.strip()
                if line.startswith('TASK_TYPE:'):
                    analysis['task_type'] = line.split(':', 1)[1].strip().lower()
                elif line.startswith('PRIORITY:'):
                    analysis['priority'] = line.split(':', 1)[1].strip().lower()
                elif line.startswith('REQUIRES_APPROVAL:'):
                    approval = line.split(':', 1)[1].strip().lower()
                    analysis['requires_approval'] = approval in ['yes', 'true']
                elif line.startswith('RISKS:'):
                    analysis['risks'] = line.split(':', 1)[1].strip()
                elif line and line[0].isdigit() and '.' in line[:3]:
                    # Action item
                    action = line.split('.', 1)[1].strip()
                    if action:
                        analysis['actions'].append(action)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing task {task_file.name}: {e}")
            return None

    def create_plan(self, task_file: Path, analysis: dict) -> Path:
        """Create a Plan.md file based on analysis"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plan_name = f"PLAN_{task_file.stem}_{timestamp}.md"
            plan_path = self.plans_dir / plan_name

            # Generate plan content
            plan_content = f"""---
type: plan
source_task: {task_file.name}
task_type: {analysis['task_type']}
priority: {analysis['priority']}
requires_approval: {analysis['requires_approval']}
created: {datetime.now().isoformat()}
status: pending
---

# Task Plan: {task_file.stem}

## Original Task
See: `Needs_Action/{task_file.name}`

## Analysis
- **Type:** {analysis['task_type']}
- **Priority:** {analysis['priority']}
- **Approval Required:** {'Yes' if analysis['requires_approval'] else 'No'}

## Proposed Actions

"""

            # Add action items as checkboxes
            for i, action in enumerate(analysis['actions'], 1):
                plan_content += f"{i}. [ ] {action}\n"

            plan_content += f"""

## Risks & Concerns
{analysis['risks']}

## Next Steps
"""

            if analysis['requires_approval']:
                plan_content += """
This task requires human approval before execution.
An approval request will be created in `Pending_Approval/`.

To proceed:
1. Review the approval request
2. Move it to `Approved/` folder
3. The system will execute the approved actions
"""
            else:
                plan_content += """
This task can be executed automatically.
The system will process it based on the action plan above.
"""

            plan_content += f"""

---
*Generated by Qwen Reasoning Engine at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

            plan_path.write_text(plan_content)
            logger.info(f"📋 Created plan: {plan_name}")

            return plan_path

        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            return None

    def create_approval_request(self, task_file: Path, analysis: dict) -> Path:
        """Create an approval request for sensitive actions"""
        try:
            # Determine subdirectory based on task type
            task_type = analysis['task_type']
            if task_type == 'email':
                approval_dir = self.pending_approval_dir / 'emails'
            elif task_type == 'social_media':
                # Check if it's LinkedIn or Twitter
                content = task_file.read_text().lower()
                if 'linkedin' in content:
                    approval_dir = self.pending_approval_dir / 'linkedin'
                elif 'twitter' in content:
                    approval_dir = self.pending_approval_dir / 'twitter'
                else:
                    approval_dir = self.pending_approval_dir / 'social_media'
            elif task_type == 'payment':
                approval_dir = self.pending_approval_dir / 'payments'
            else:
                approval_dir = self.pending_approval_dir / 'general'

            approval_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            approval_name = f"APPROVAL_{task_file.stem}_{timestamp}.md"
            approval_path = approval_dir / approval_name

            # Read original task content
            task_content = task_file.read_text()

            approval_content = f"""---
type: approval_request
source_task: {task_file.name}
task_type: {analysis['task_type']}
priority: {analysis['priority']}
created: {datetime.now().isoformat()}
status: pending_approval
---

# Approval Required: {task_file.stem}

## Task Details
{task_content}

## Proposed Actions
"""

            for i, action in enumerate(analysis['actions'], 1):
                approval_content += f"{i}. {action}\n"

            approval_content += f"""

## Risks & Concerns
{analysis['risks']}

## To Approve
Move this file to `Approved/{approval_dir.name}/` folder

## To Reject
Move this file to `Rejected/` folder or delete it

---
*Approval request generated by Qwen Reasoning Engine*
*Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

            approval_path.write_text(approval_content)
            logger.info(f"✋ Created approval request: {approval_name}")

            return approval_path

        except Exception as e:
            logger.error(f"Error creating approval request: {e}")
            return None

    def process_needs_action(self):
        """Process all files in Needs_Action folder"""
        try:
            if not self.needs_action_dir.exists():
                return

            # Get all markdown files
            task_files = list(self.needs_action_dir.glob('*.md'))

            if not task_files:
                return

            logger.info(f"🧠 Processing {len(task_files)} tasks...")

            for task_file in task_files:
                try:
                    logger.info(f"   Analyzing: {task_file.name}")

                    # Analyze the task
                    analysis = self.analyze_task(task_file)

                    if not analysis:
                        logger.warning(f"   ⚠️  Failed to analyze {task_file.name}")
                        continue

                    # Create plan
                    plan_path = self.create_plan(task_file, analysis)

                    if not plan_path:
                        logger.warning(f"   ⚠️  Failed to create plan for {task_file.name}")
                        continue

                    # Create approval request if needed
                    if analysis['requires_approval']:
                        approval_path = self.create_approval_request(task_file, analysis)
                        if approval_path:
                            logger.info(f"   ✅ Task requires approval: {task_file.name}")
                    else:
                        logger.info(f"   ✅ Task can be auto-executed: {task_file.name}")

                    # Move original task to Done (it's been processed)
                    done_path = self.done_dir / 'processed_tasks'
                    done_path.mkdir(parents=True, exist_ok=True)
                    task_file.rename(done_path / task_file.name)

                    logger.info(f"   📦 Moved {task_file.name} to Done/processed_tasks/")

                except Exception as e:
                    logger.error(f"   ❌ Error processing {task_file.name}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error in process_needs_action: {e}")

    def run(self):
        """Main loop - continuously process tasks"""
        logger.info("🚀 Qwen Reasoning Engine started")
        logger.info(f"   Checking every {self.check_interval} seconds")
        logger.info(f"   Watching: {self.needs_action_dir}")

        while True:
            try:
                self.process_needs_action()
                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                logger.info("⏹️  Qwen Reasoning Engine stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(self.check_interval)


if __name__ == '__main__':
    # Get vault path from environment or use default
    vault_path = os.getenv('AI_EMPLOYEE_VAULT', '/mnt/d/AI/Personal-AI-Employee/AI_Employee_Vault')

    # Create and run the reasoning engine
    engine = QwenReasoningEngine(vault_path, check_interval=30)
    engine.run()
