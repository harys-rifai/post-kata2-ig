#!/usr/bin/env bash
# Run Django Instagram AI - kills existing processes first

echo "==================================="
echo "START DJANGO INSTAGRAM AI"
echo "==================================="

# Kill existing processes
echo "Killing existing processes..."

# Kill any process on port 809
if lsof -i :809 -t >/dev/null 2>&1; then
    kill $(lsof -i :809 -t) 2>/dev/null || true
fi

# Kill any existing celery workers
pkill -f "celery.*config worker" 2>/dev/null || true
pkill -f "celery.*config beat" 2>/dev/null || true
pkill -f "celery-beat" 2>/dev/null || true

# Kill any existing Django runserver
pkill -f "python.*manage.py runserver" 2>/dev/null || true

# Start Redis (only if not already running)
if ! redis-cli ping &> /dev/null; then
    echo "Starting Redis..."
    redis-server --daemonize yes 2>/dev/null
    echo "Redis started."
    sleep 1
fi

# Start Celery Worker in background
echo "Starting Celery Worker..."
celery -A config worker -l info --detach

# Start Celery Beat in background
echo "Starting Celery Beat..."
celery -A config beat -l info --detach

# Start Django (foreground)
echo "Starting Django on port 809..."
python manage.py runserver 0.0.0.0:809