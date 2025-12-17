#!/bin/bash
set -e

echo "Waiting for database to be ready..."
# Simple wait loop - docker-compose depends_on handles most of this
# but we add a small delay to ensure DB is fully ready
sleep 3

# Retry loop for migrations (in case DB isn't quite ready)
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  echo "Attempting to run migrations (attempt $((RETRY_COUNT + 1))/$MAX_RETRIES)..."
  if alembic upgrade head; then
    echo "Migrations completed successfully!"
    break
  else
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
      echo "Migration failed, retrying in 2 seconds..."
      sleep 2
    else
      echo "Failed to run migrations after $MAX_RETRIES attempts"
      exit 1
    fi
  fi
done

echo "Starting application..."
# Start the application
exec "$@"

