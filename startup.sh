#!/bin/bash
# startup.sh 

# 1. Total port cleanup
echo "Releasing ports 8000 and 8001..."
lsof -ti:8000,8001 | xargs kill -9 2>/dev/null

# 2. Environment configuration
export CDA_SECRET_KEY="internal_development_secret_key_fixed_32_chars"
export PYTHONPATH=$(pwd)
source .venv/bin/activate

echo "--------------------------------------"
echo "Starting CDA Services..."
echo "--------------------------------------"

# 3. Launch Kernel Service
python3 -m uvicorn cda.kernel.engine:app --port 8000 --host 127.0.0.1 > kernel.log 2>&1 &
KERNEL_PID=$!

# 4. Launch Gate Service
python3 -m uvicorn cda.gate.engine:app --port 8001 --host 127.0.0.1 > gate.log 2>&1 &
GATE_PID=$!

echo "Waiting 5 seconds for services to respond..."
sleep 5

# 5. Health Check (Crucial)
if ! ps -p $KERNEL_PID > /dev/null; then
    echo "X KERNEL FAILED. Error detected:"
    cat kernel.log
    exit 1
fi

if ! ps -p $GATE_PID > /dev/null; then
    echo "X GATE FAILED. Error detected:"
    cat gate.log
    exit 1
fi

# 6. Run Integration Tests
echo "Executing Integration Tests..."
python3 cda/tests/test_integration.py

# 7. Final Cleanup
echo "--------------------------------------"
echo "Shutting down services..."
kill -9 $KERNEL_PID $GATE_PID 2>/dev/null
echo "Process finished."