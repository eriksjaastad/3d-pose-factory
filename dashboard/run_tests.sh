#!/bin/bash
###############################################################################
# Dashboard Test Runner
#
# USAGE (copy-paste ready):
#     cd /Users/eriksjaastad/projects/3D\ Pose\ Factory/dashboard
#     source venv/bin/activate
#     ./run_tests.sh
###############################################################################

# Activate venv if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    source venv/bin/activate
fi

# Run all tests
echo "============================="
echo "Running Dashboard Tests"
echo "============================="
python -m pytest tests/ -v --tb=short

echo ""
echo "============================="
echo "Test Summary"
echo "============================="
python -m pytest tests/ --tb=no -q

