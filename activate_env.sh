#!/bin/bash
# Activate Virtual Environment Helper
# Source this file to activate the virtual environment

# Activate the virtual environment
source /home/arifabbas-ubuntu/ai-employee-env/bin/activate

echo "✓ Virtual environment activated"
echo "Python: $(python --version)"
echo "Location: $(which python)"
echo ""
echo "You can now run:"
echo "  python test_automation_systems.py"
echo "  python test_multi_agent_system.py"
echo "  python test_learning_systems.py"
echo ""
echo "Or use any Python scripts with the correct dependencies."
