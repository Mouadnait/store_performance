#!/bin/bash
cd /mnt/h/Mine/Back-end/store_performance/performance

PYTHON_BIN="/mnt/h/Mine/Back-end/store_performance/.store/bin/python"

echo "Starting Celery Worker..."
$PYTHON_BIN -m celery -A performance worker -l info &
WORKER_PID=$!

echo "Starting Celery Beat..."
$PYTHON_BIN -m celery -A performance beat -l info &
BEAT_PID=$!

echo "Celery Worker (PID: $WORKER_PID) and Beat (PID: $BEAT_PID) started"
echo "To stop: kill $WORKER_PID $BEAT_PID"
