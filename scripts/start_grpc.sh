#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GRPC_DIR="$PROJECT_ROOT/grpc-test-vkr-main/vkr-glossary-grpc-project/glossary-grpc/glossary-service"

cd "$GRPC_DIR" || exit 1

if [ ! -d "venv" ] || [ ! -f "venv/bin/python3" ] || ! venv/bin/python3 --version >/dev/null 2>&1; then
    rm -rf venv
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Ошибка: не удалось создать venv. Установите python3-venv: sudo apt install python3-venv"
        exit 1
    fi
fi

venv/bin/python3 -m pip install --upgrade pip --quiet

if ! venv/bin/python3 -c "import grpc" 2>/dev/null; then
    venv/bin/pip install -r requirements.txt
fi

if [ ! -f "glossary_pb2.py" ] || [ ! -f "glossary_pb2_grpc.py" ]; then
    venv/bin/python3 -m grpc_tools.protoc -I ./protobufs --python_out=. --grpc_python_out=. ./protobufs/glossary.proto
fi

echo "gRPC: 127.0.0.1:50052"
venv/bin/python3 glossary.py

