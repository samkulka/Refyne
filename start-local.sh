#!/bin/bash

# Start Refyne locally - API + UI

echo "🚀 Starting Refyne..."
echo ""

# Start Python API
echo "📡 Starting Python API on http://localhost:8000"
python3 -m uvicorn api.main:app --reload --port 8000 &
API_PID=$!

# Wait for API to start
sleep 3

# Start Next.js UI
echo "🎨 Starting Next.js UI on http://localhost:3000"
npm run dev &
UI_PID=$!

echo ""
echo "✅ Refyne is running!"
echo ""
echo "  API:  http://localhost:8000"
echo "  Docs: http://localhost:8000/docs"
echo "  UI:   http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user to stop
trap "kill $API_PID $UI_PID; exit" INT
wait
