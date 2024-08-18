#!/bin/sh
PYTHONPATH=$PYTHONPATH:./apainvoice gunicorn webapp:app --reload -w 1 -k uvicorn.workers.UvicornWorker

