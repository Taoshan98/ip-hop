#!/bin/sh
set -e

echo "Starting IP-HOP Application..."

# Initialize database if it doesn't exist
if [ ! -f /app/backend/database/ip_hop.db ]; then
    echo "Initializing database..."
    cd /app/backend && python scripts/init_db.py
fi

# Start backend in background
echo "Starting backend server..."
cd /app/backend && uvicorn app.main:app --host 0.0.0.0 --port 8001 &

# Start frontend
echo "Starting frontend server..."
cd /app/frontend && npm start -- -p 3000 &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
