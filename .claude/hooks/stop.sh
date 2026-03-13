#!/bin/bash
# Ralph Wiggum Stop Hook
# Prevents Claude from exiting until task is complete

set -e

# Configuration
VAULT_PATH="${VAULT_PATH:-/mnt/d/AI/Personal-AI-Employee/AI_Employee_Vault}"
STATE_FILE="${STATE_FILE:-/tmp/ralph_wiggum_state.json}"
MAX_ITERATIONS="${MAX_ITERATIONS:-10}"
MAX_TIME_MINUTES="${MAX_TIME_MINUTES:-30}"

# Logging
LOG_FILE="/tmp/ralph_wiggum.log"
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "Stop hook triggered"

# Check if Ralph Wiggum mode is active
if [ ! -f "$STATE_FILE" ]; then
    log "No state file - allowing exit (not in Ralph mode)"
    exit 0
fi

# Read state using jq if available, otherwise use grep/sed
if command -v jq &> /dev/null; then
    TASK_FILE=$(jq -r '.task_file' "$STATE_FILE")
    TASK_NAME=$(jq -r '.task_name' "$STATE_FILE")
    CURRENT_ITERATION=$(jq -r '.iteration' "$STATE_FILE")
    START_TIME=$(jq -r '.start_time' "$STATE_FILE")
    COMPLETION_STRATEGY=$(jq -r '.completion_strategy' "$STATE_FILE")
else
    # Fallback parsing without jq
    TASK_FILE=$(grep -o '"task_file":"[^"]*"' "$STATE_FILE" | cut -d'"' -f4)
    TASK_NAME=$(grep -o '"task_name":"[^"]*"' "$STATE_FILE" | cut -d'"' -f4)
    CURRENT_ITERATION=$(grep -o '"iteration":[0-9]*' "$STATE_FILE" | cut -d':' -f2)
    START_TIME=$(grep -o '"start_time":[0-9]*' "$STATE_FILE" | cut -d':' -f2)
    COMPLETION_STRATEGY=$(grep -o '"completion_strategy":"[^"]*"' "$STATE_FILE" | cut -d'"' -f4)
fi

log "Task: $TASK_NAME (iteration $CURRENT_ITERATION)"

# Safety check: Max iterations
if [ "$CURRENT_ITERATION" -ge "$MAX_ITERATIONS" ]; then
    log "Max iterations ($MAX_ITERATIONS) reached - forcing exit"
    rm -f "$STATE_FILE"
    echo "⚠️  Ralph Wiggum: Max iterations reached. Task may be incomplete."
    exit 0
fi

# Safety check: Max time
CURRENT_TIME=$(date +%s)
ELAPSED_MINUTES=$(( (CURRENT_TIME - START_TIME) / 60 ))
if [ "$ELAPSED_MINUTES" -ge "$MAX_TIME_MINUTES" ]; then
    log "Max time ($MAX_TIME_MINUTES minutes) reached - forcing exit"
    rm -f "$STATE_FILE"
    echo "⚠️  Ralph Wiggum: Max time reached. Task may be incomplete."
    exit 0
fi

# Check completion based on strategy
case "$COMPLETION_STRATEGY" in
    "file_movement")
        # Check if task file moved to /Done
        if [ -n "$TASK_FILE" ]; then
            TASK_BASENAME=$(basename "$TASK_FILE")
            if [ -f "$VAULT_PATH/Done/$TASK_BASENAME" ]; then
                log "Task complete - file moved to Done"
                rm -f "$STATE_FILE"
                echo "✅ Ralph Wiggum: Task complete!"
                exit 0
            fi
        fi
        ;;

    "promise")
        # Check for completion promise in Claude's output
        # This requires capturing Claude's last output
        LAST_OUTPUT="${LAST_OUTPUT:-/tmp/claude_last_output.txt}"
        if [ -f "$LAST_OUTPUT" ] && grep -q "<promise>TASK_COMPLETE</promise>" "$LAST_OUTPUT"; then
            log "Task complete - promise found"
            rm -f "$STATE_FILE"
            echo "✅ Ralph Wiggum: Task complete!"
            exit 0
        fi
        ;;

    "empty_folder")
        # Check if Needs_Action folder is empty
        NEEDS_ACTION="$VAULT_PATH/Needs_Action"
        if [ -z "$(ls -A $NEEDS_ACTION 2>/dev/null)" ]; then
            log "Task complete - Needs_Action empty"
            rm -f "$STATE_FILE"
            echo "✅ Ralph Wiggum: All tasks processed!"
            exit 0
        fi
        ;;
esac

# Task not complete - continue loop
log "Task incomplete - continuing loop"

# Increment iteration
NEXT_ITERATION=$((CURRENT_ITERATION + 1))

# Update state file
if command -v jq &> /dev/null; then
    jq ".iteration = $NEXT_ITERATION" "$STATE_FILE" > "${STATE_FILE}.tmp"
    mv "${STATE_FILE}.tmp" "$STATE_FILE"
else
    # Fallback: manual update
    sed -i "s/\"iteration\":[0-9]*/\"iteration\":$NEXT_ITERATION/" "$STATE_FILE"
fi

# Provide feedback to Claude
echo "🔄 Ralph Wiggum: Task not complete. Continuing... (iteration $NEXT_ITERATION/$MAX_ITERATIONS)"
echo ""
echo "Continue working on: $TASK_NAME"
echo "Check your progress and complete any remaining steps."
echo ""

# Exit with non-zero to prevent Claude from stopping
exit 1
