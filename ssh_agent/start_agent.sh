#!/bin/bash
###############################################################################
# Start SSH Agent
#
# This agent lets Claude run SSH commands on the RunPod
# by writing to ops_queue/requests.jsonl and reading from
# ops_queue/results.jsonl
###############################################################################

cd "$(dirname "$0")"

echo "📡 Starting SSH Agent..."
echo ""
echo "Claude can now run SSH commands on RunPod!"
echo "The agent will poll ops_queue/requests.jsonl for new commands."
echo ""
echo "Press Ctrl+C to stop the agent."
echo ""

# Check if dependencies are installed
if ! python3 -c "import paramiko, yaml" 2>/dev/null; then
    echo "⚠️  Missing dependencies! Installing..."
    pip3 install -r requirements.txt
fi

# Run the agent
python3 agent.py

