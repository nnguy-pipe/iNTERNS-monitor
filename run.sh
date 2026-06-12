#!/bin/bash

# --- Start simulator ---
echo "Starting simulator..."
python3 infrastructure_sim/infrastructure_simulator_daemon.py --port 9999 &
SIM_PID=$!

# --- Start backend ---
echo "Starting backend..."
python3 -m uvicorn src.api.main:app --reload &
BACKEND_PID=$!

# --- Start frontend ---
echo "Starting frontend..."
npm run dev &
FRONTEND_PID=$!
cd ..

# --- Cleanup on exit ---
trap "echo 'Stopping...'; kill $BACKEND_PID $SIM_PID $FRONTEND_PID" EXIT

wait
