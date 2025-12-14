#!/bin/bash

ok=1

curl -s -f http://127.0.0.1:8000/api/health >/dev/null 2>&1 || ok=0
timeout 1 bash -c "echo > /dev/tcp/127.0.0.1/50052" >/dev/null 2>&1 || ok=0

if [ "$ok" -eq 1 ]; then
  echo "OK"
  exit 0
fi

echo "FAIL"
exit 1

