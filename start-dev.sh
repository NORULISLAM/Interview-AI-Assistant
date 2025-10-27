#!/bin/bash

echo "Starting Interview AI Assistant Development Environment..."
echo

echo "[1/4] Starting Docker services (PostgreSQL, Redis, Qdrant)..."
docker-compose up -d postgres redis qdrant
sleep 10

echo "[2/4] Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

echo "[3/4] Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "[4/4] Starting all services..."
echo
echo "Backend API: http://localhost:8000"
echo "Frontend App: http://localhost:3000"
echo "ASR Service: http://localhost:8001"
echo
echo "Starting services in parallel..."

# Start backend API
gnome-terminal --title="Backend API" -- bash -c "cd backend && python main.py; exec bash" &
sleep 5

# Start ASR service
gnome-terminal --title="ASR Service" -- bash -c "cd backend && python asr_service.py; exec bash" &
sleep 5

# Start frontend
gnome-terminal --title="Frontend App" -- bash -c "cd frontend && npm run dev; exec bash" &

echo
echo "All services started! Check the opened terminals for any errors."
echo
echo "To stop all services, close the terminal windows or press Ctrl+C."
