#!/bin/sh

# Start cron in the background
cron

# Start uvicorn as the main process
exec uvicorn --reload webapp:app --host 0.0.0.0
