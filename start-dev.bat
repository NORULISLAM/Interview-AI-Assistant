@echo off
echo Starting Interview AI Assistant Development Environment...
echo.

echo [1/4] Starting Docker services (PostgreSQL, Redis, Qdrant)...
docker-compose up -d postgres redis qdrant
timeout /t 10 /nobreak > nul

echo [2/4] Installing backend dependencies...
cd backend
pip install -r requirements.txt
cd ..

echo [3/4] Installing frontend dependencies...
cd frontend
npm install
cd ..

echo [4/4] Starting all services...
echo.
echo Backend API: http://localhost:8000
echo Frontend App: http://localhost:3000
echo ASR Service: http://localhost:8001
echo.
echo Starting services in parallel...

start "Backend API" cmd /k "cd backend && python main.py"
timeout /t 5 /nobreak > nul

start "ASR Service" cmd /k "cd backend && python asr_service.py"
timeout /t 5 /nobreak > nul

start "Frontend App" cmd /k "cd frontend && npm run dev"

echo.
echo All services started! Check the opened windows for any errors.
echo.
echo To stop all services, close the terminal windows or press Ctrl+C.
pause
