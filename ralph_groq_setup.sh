#!/bin/bash
# Ralph Wiggum - Groq Setup Script
# Configures and launches Groq-powered autonomous agent

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
VAULT_PATH="/mnt/d/AI/Personal-AI-Employee/AI_Employee_Vault"
STRATEGY="empty_folder"
MAX_ITERATIONS=10
MAX_TIME=30
TASK_FILE=""
MODEL="llama-3.3-70b-versatile"

# Help message
show_help() {
    cat << EOF
Ralph Wiggum - Groq-Powered Autonomous Agent

Usage: $0 [OPTIONS] "TASK_DESCRIPTION"

Options:
  -s, --strategy STRATEGY    Completion strategy (required)
                            file_movement | promise | empty_folder
  -f, --file FILE           Task file path (for file_movement)
  -i, --iterations N        Max iterations (default: 10)
  -t, --time N              Max time in minutes (default: 30)
  -m, --model MODEL         Groq model (default: llama-3.3-70b-versatile)
  -v, --vault PATH          Vault path (default: $VAULT_PATH)
  -h, --help                Show this help message

Completion Strategies:
  file_movement  - Task complete when file moved to Done/
  empty_folder   - Task complete when Needs_Action/ is empty
  promise        - Task complete when agent outputs <promise>TASK_COMPLETE</promise>

Examples:
  # Process all tasks in Needs_Action
  $0 -s empty_folder "Process all tasks in Needs_Action/"

  # Process specific task file
  $0 -s file_movement -f "Needs_Action/TASK_001.md" "Complete TASK_001"

  # Generate content with promise
  $0 -s promise "Create 3 LinkedIn posts and output completion promise"

Environment Variables:
  GROQ_API_KEY   - Your Groq API key (required)
                   Get free key at: https://console.groq.com

EOF
}

# Parse arguments
TASK_DESC=""
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--strategy)
            STRATEGY="$2"
            shift 2
            ;;
        -f|--file)
            TASK_FILE="$2"
            shift 2
            ;;
        -i|--iterations)
            MAX_ITERATIONS="$2"
            shift 2
            ;;
        -t|--time)
            MAX_TIME="$2"
            shift 2
            ;;
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        -v|--vault)
            VAULT_PATH="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            TASK_DESC="$1"
            shift
            ;;
    esac
done

# Validate inputs
if [ -z "$TASK_DESC" ]; then
    echo -e "${RED}Error: Task description required${NC}"
    show_help
    exit 1
fi

if [ -z "$GROQ_API_KEY" ]; then
    echo -e "${RED}Error: GROQ_API_KEY environment variable not set${NC}"
    echo -e "${YELLOW}Get your free API key at: https://console.groq.com${NC}"
    exit 1
fi

if [ ! -d "$VAULT_PATH" ]; then
    echo -e "${RED}Error: Vault path does not exist: $VAULT_PATH${NC}"
    exit 1
fi

# Display configuration
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}  ${GREEN}Ralph Wiggum - Groq-Powered Autonomous Agent${NC}         ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Configuration:${NC}"
echo -e "  Task: ${GREEN}$TASK_DESC${NC}"
echo -e "  Strategy: ${GREEN}$STRATEGY${NC}"
echo -e "  Model: ${GREEN}$MODEL${NC}"
echo -e "  Max Iterations: ${GREEN}$MAX_ITERATIONS${NC}"
echo -e "  Max Time: ${GREEN}$MAX_TIME minutes${NC}"
echo -e "  Vault: ${GREEN}$VAULT_PATH${NC}"
if [ -n "$TASK_FILE" ]; then
    echo -e "  Task File: ${GREEN}$TASK_FILE${NC}"
fi
echo ""

# Build command
CMD="python3 ralph_groq_orchestrator.py"
CMD="$CMD --vault '$VAULT_PATH'"
CMD="$CMD --strategy '$STRATEGY'"
CMD="$CMD --max-iterations $MAX_ITERATIONS"
CMD="$CMD --max-time $MAX_TIME"
CMD="$CMD --model '$MODEL'"
if [ -n "$TASK_FILE" ]; then
    CMD="$CMD --task-file '$TASK_FILE'"
fi
CMD="$CMD '$TASK_DESC'"

# Confirm execution
echo -e "${YELLOW}Ready to start Ralph Wiggum loop${NC}"
echo -e "${YELLOW}Press Enter to continue, Ctrl+C to cancel...${NC}"
read

# Execute
echo -e "${GREEN}🚀 Starting Ralph Wiggum...${NC}"
echo ""

eval $CMD

# Check result
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Ralph Wiggum completed successfully!${NC}"
else
    echo ""
    echo -e "${RED}⚠️  Ralph Wiggum exited with errors${NC}"
    echo -e "${YELLOW}Check logs at: $VAULT_PATH/Logs/${NC}"
fi
