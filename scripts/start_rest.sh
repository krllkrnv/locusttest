#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/mindmap-vkr-main/backend"

cd "$BACKEND_DIR" || exit 1

if [ ! -d "venv" ] || [ ! -f "venv/bin/python3" ] || ! venv/bin/python3 --version >/dev/null 2>&1; then
    rm -rf venv
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Ошибка: не удалось создать venv. Установите python3-venv: sudo apt install python3-venv"
        exit 1
    fi
fi

venv/bin/python3 -m pip install --upgrade pip --quiet

if ! venv/bin/python3 -c "import fastapi" 2>/dev/null || ! venv/bin/python3 -c "import uvicorn" 2>/dev/null; then
    venv/bin/pip install -r requirements.txt
fi

if ! venv/bin/python3 -m uvicorn --help >/dev/null 2>&1; then
    venv/bin/pip install --force-reinstall -r requirements.txt
fi

echo "REST: http://127.0.0.1:8000"
venv/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

