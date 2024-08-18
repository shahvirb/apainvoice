#!/bin/sh
uvicorn webapp:app --reload --app-dir apainvoice/ --log-level debug
