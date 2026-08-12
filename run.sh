#!/bin/bash
# Script Peluncur Image Upscaler & Font Sharpener Web App

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=================================================="
echo "⚡ Font & Image Upscaler Web App Launcher ⚡"
echo "=================================================="

# Check virtualenv
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install -r requirements.txt
fi

echo "Starting Flask Web App..."
echo "Akses aplikasi di browser: http://127.0.0.1:5000"
echo "Tekan Ctrl+C untuk menghentikan aplikasi."
echo "=================================================="

./venv/bin/python3 app.py
