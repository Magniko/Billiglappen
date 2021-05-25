#!/bin/bash

python scraper_main.py &
uvicorn app.api.billiglappen_api:app --host 0.0.0.0 --port=${PORT:-5000}