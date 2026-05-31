#!/usr/bin/env bash
set -e
echo "Starting Improved AI Resume Analyzer..."
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
