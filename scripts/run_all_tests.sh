#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Run all tests (REST + gRPC)"
if ! "$SCRIPT_DIR/check_services.sh"; then
    exit 1
fi

"$SCRIPT_DIR/run_test.sh" rest sanity 5 1 2m
"$SCRIPT_DIR/run_test.sh" grpc sanity 5 1 2m

"$SCRIPT_DIR/run_test.sh" rest normal 50 5 5m
"$SCRIPT_DIR/run_test.sh" grpc normal 50 5 5m

"$SCRIPT_DIR/run_test.sh" rest stress 100 10 3m
"$SCRIPT_DIR/run_test.sh" grpc stress 100 10 3m

"$SCRIPT_DIR/run_test.sh" rest stability 50 5 15m
"$SCRIPT_DIR/run_test.sh" grpc stability 50 5 15m
echo "Done"

