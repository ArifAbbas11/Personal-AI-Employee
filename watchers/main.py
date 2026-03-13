#!/usr/bin/env python3
"""
AI Employee Watchers - Main Orchestrator
Runs all watchers in Docker container
"""

import os
import sys
import time
import logging
import signal
from pathlib import Path
from threading import Thread

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import watchers
try:
    from watchers.gmail_watcher import GmailWatcher
except ImportError:
    GmailWatcher = None

try:
    from watchers.filesystem_watcher import FilesystemWatcher
except ImportError:
    FilesystemWatcher = None

try:
    from watchers.gmail_auto_responder import GmailAutoResponder
except ImportError:
    GmailAutoResponder = None

try:
    from watchers.email_response_generator import EmailResponseGenerator
except ImportError:
    EmailResponseGenerator = None

try:
    from watchers.post_generator import PostGenerator
except ImportError:
    PostGenerator = None

try:
    from watchers.social_media_auto_poster import SocialMediaAutoPoster
except ImportError:
    SocialMediaAutoPoster = None

# Disabled: QwenReasoningEngine auto-processes emails too quickly
# Use Ralph Groq for manual email processing instead
# try:
#     from watchers.qwen_reasoning_engine import QwenReasoningEngine
# except ImportError:
#     QwenReasoningEngine = None
QwenReasoningEngine = None

# Configure logging
log_path = os.getenv('LOG_PATH', '/app/logs')
os.makedirs(log_path, exist_ok=True)

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'{log_path}/orchestrator.log')
    ]
)

logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_flag = False

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global shutdown_flag
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_flag = True

def run_watcher(watcher_class, *args, **kwargs):
    """Run a watcher in a thread"""
    watcher_name = watcher_class.__name__

    try:
        watcher = watcher_class(*args, **kwargs)
        logger.info(f"Starting {watcher_name}...")

        while not shutdown_flag:
            try:
                # Run one iteration
                items = watcher.check_for_updates()
                if items:
                    logger.info(f"{watcher_name}: Found {len(items)} new items")
                    for item in items:
                        # Gmail returns dict with 'id', extract it
                        if isinstance(item, dict) and 'id' in item:
                            watcher.create_action_file(item['id'])
                        else:
                            watcher.create_action_file(item)

                # Sleep for check interval
                time.sleep(watcher.check_interval)

            except Exception as e:
                logger.error(f"Error in {watcher_name}: {e}", exc_info=True)
                time.sleep(60)  # Wait before retry

    except Exception as e:
        logger.error(f"Fatal error in {watcher_name}: {e}", exc_info=True)

def main():
    """Main orchestrator"""
    logger.info("🚀 AI Employee Watchers Starting...")

    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Get configuration from environment
    vault_path = os.getenv('VAULT_PATH', '/vault')
    gmail_creds = os.getenv('GMAIL_CREDENTIALS_PATH')

    # Verify vault exists
    if not Path(vault_path).exists():
        logger.error(f"Vault not found at {vault_path}")
        sys.exit(1)

    logger.info(f"Using vault at: {vault_path}")

    # Start watchers in threads
    threads = []

    # Filesystem Watcher
    if FilesystemWatcher:
        try:
            thread = Thread(
                target=run_watcher,
                args=(FilesystemWatcher, vault_path),
                daemon=True,
                name="FilesystemWatcher"
            )
            thread.start()
            threads.append(thread)
            logger.info("✅ Filesystem Watcher started")
        except Exception as e:
            logger.error(f"Failed to start Filesystem Watcher: {e}")
    else:
        logger.warning("⚠️  FilesystemWatcher not available")

    # Gmail Watcher (if credentials available)
    if GmailWatcher and gmail_creds and Path(gmail_creds).exists():
        try:
            thread = Thread(
                target=run_watcher,
                args=(GmailWatcher, vault_path, gmail_creds),
                daemon=True,
                name="GmailWatcher"
            )
            thread.start()
            threads.append(thread)
            logger.info("✅ Gmail Watcher started")
        except Exception as e:
            logger.error(f"Failed to start Gmail Watcher: {e}")
    else:
        logger.warning("⚠️  Gmail credentials not found, skipping Gmail Watcher")

    # Gmail Auto-Responder (if credentials available)
    if GmailAutoResponder and gmail_creds and Path(gmail_creds).exists():
        try:
            def run_auto_responder():
                """Run Gmail Auto-Responder"""
                try:
                    responder = GmailAutoResponder()
                    logger.info("Starting GmailAutoResponder...")

                    while not shutdown_flag:
                        try:
                            responder.check_approved_emails()
                            time.sleep(60)  # Check every 60 seconds
                        except Exception as e:
                            logger.error(f"Error in GmailAutoResponder: {e}", exc_info=True)
                            time.sleep(60)

                except Exception as e:
                    logger.error(f"Fatal error in GmailAutoResponder: {e}", exc_info=True)

            thread = Thread(
                target=run_auto_responder,
                daemon=True,
                name="GmailAutoResponder"
            )
            thread.start()
            threads.append(thread)
            logger.info("✅ Gmail Auto-Responder started")
        except Exception as e:
            logger.error(f"Failed to start Gmail Auto-Responder: {e}")
    else:
        logger.warning("⚠️  Gmail Auto-Responder not available")

    # Email Response Generator
    if EmailResponseGenerator:
        try:
            def run_response_generator():
                """Run Email Response Generator"""
                try:
                    generator = EmailResponseGenerator(vault_path)
                    logger.info("Starting EmailResponseGenerator...")

                    while not shutdown_flag:
                        try:
                            generator.process_email_actions()
                            time.sleep(30)  # Check every 30 seconds
                        except Exception as e:
                            logger.error(f"Error in EmailResponseGenerator: {e}", exc_info=True)
                            time.sleep(30)

                except Exception as e:
                    logger.error(f"Fatal error in EmailResponseGenerator: {e}", exc_info=True)

            thread = Thread(
                target=run_response_generator,
                daemon=True,
                name="EmailResponseGenerator"
            )
            thread.start()
            threads.append(thread)
            logger.info("✅ Email Response Generator started")
        except Exception as e:
            logger.error(f"Failed to start Email Response Generator: {e}")
    else:
        logger.warning("⚠️  Email Response Generator not available")

    # Post Generator
    if PostGenerator:
        try:
            def run_post_generator():
                """Run Post Generator"""
                try:
                    generator = PostGenerator(vault_path)
                    logger.info("Starting PostGenerator...")

                    while not shutdown_flag:
                        try:
                            generator.process_topic_files()
                            time.sleep(30)  # Check every 30 seconds
                        except Exception as e:
                            logger.error(f"Error in PostGenerator: {e}", exc_info=True)
                            time.sleep(30)

                except Exception as e:
                    logger.error(f"Fatal error in PostGenerator: {e}", exc_info=True)

            thread = Thread(
                target=run_post_generator,
                daemon=True,
                name="PostGenerator"
            )
            thread.start()
            threads.append(thread)
            logger.info("✅ Post Generator started")
        except Exception as e:
            logger.error(f"Failed to start Post Generator: {e}")
    else:
        logger.warning("⚠️  Post Generator not available")

    # Social Media Auto-Poster
    if SocialMediaAutoPoster:
        try:
            def run_social_media_poster():
                """Run Social Media Auto-Poster"""
                try:
                    poster = SocialMediaAutoPoster(vault_path)
                    logger.info("Starting SocialMediaAutoPoster...")

                    while not shutdown_flag:
                        try:
                            poster.process_approved_posts()
                            time.sleep(60)  # Check every 60 seconds
                        except Exception as e:
                            logger.error(f"Error in SocialMediaAutoPoster: {e}", exc_info=True)
                            time.sleep(60)

                except Exception as e:
                    logger.error(f"Fatal error in SocialMediaAutoPoster: {e}", exc_info=True)

            thread = Thread(
                target=run_social_media_poster,
                daemon=True,
                name="SocialMediaAutoPoster"
            )
            thread.start()
            threads.append(thread)
            logger.info("✅ Social Media Auto-Poster started")
        except Exception as e:
            logger.error(f"Failed to start Social Media Auto-Poster: {e}")
    else:
        logger.warning("⚠️  Social Media Auto-Poster not available")

    # Qwen Reasoning Engine (The Brain)
    if QwenReasoningEngine:
        try:
            def run_qwen_engine():
                """Run Qwen Reasoning Engine"""
                try:
                    engine = QwenReasoningEngine(vault_path, check_interval=30)
                    logger.info("Starting QwenReasoningEngine...")

                    while not shutdown_flag:
                        try:
                            engine.process_needs_action()
                            time.sleep(30)  # Check every 30 seconds
                        except Exception as e:
                            logger.error(f"Error in QwenReasoningEngine: {e}", exc_info=True)
                            time.sleep(30)

                except Exception as e:
                    logger.error(f"Fatal error in QwenReasoningEngine: {e}", exc_info=True)

            thread = Thread(
                target=run_qwen_engine,
                daemon=True,
                name="QwenReasoningEngine"
            )
            thread.start()
            threads.append(thread)
            logger.info("✅ Qwen Reasoning Engine started (The Brain)")
        except Exception as e:
            logger.error(f"Failed to start Qwen Reasoning Engine: {e}")
    else:
        logger.warning("⚠️  Qwen Reasoning Engine not available")

    logger.info(f"🎯 All watchers started ({len(threads)} active)")

    # Keep main thread alive
    try:
        while not shutdown_flag:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")

    # Graceful shutdown
    logger.info("🛑 Shutting down watchers...")
    for thread in threads:
        thread.join(timeout=5)

    logger.info("✅ Shutdown complete")

if __name__ == '__main__':
    main()
