#!/bin/bash
# Usage: ./run_test.sh [rest|grpc] [sanity|normal|stress|stability] [users] [spawn_rate] [duration]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOADTEST_DIR="$PROJECT_ROOT/loadtest"

PROTOCOL="${1:-rest}"
SCENARIO="${2:-sanity}"
USERS="${3:-5}"
SPAWN_RATE="${4:-1}"
DURATION="${5:-2m}"

if [[ ! "$PROTOCOL" =~ ^(rest|grpc)$ ]]; then
    echo "Ошибка: протокол должен быть 'rest' или 'grpc'"
    exit 1
fi

if [[ ! "$SCENARIO" =~ ^(sanity|normal|stress|stability)$ ]]; then
    echo "Ошибка: сценарий должен быть 'sanity', 'normal', 'stress' или 'stability'"
    exit 1
fi

cd "$LOADTEST_DIR" || exit 1

if [ ! -d "venv" ]; then
    echo "Ошибка: виртуальное окружение не найдено"
    echo "Создайте venv: cd loadtest && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

source venv/bin/activate

OUTPUT_PREFIX="out/${PROTOCOL}_${SCENARIO}"

echo "Locust: $PROTOCOL $SCENARIO u=$USERS r=$SPAWN_RATE t=$DURATION"

mkdir -p out

if [ "$PROTOCOL" == "rest" ]; then
    locust -f locustfile_rest.py \
        --host http://127.0.0.1:8000 \
        -u "$USERS" \
        -r "$SPAWN_RATE" \
        -t "$DURATION" \
        --csv "$OUTPUT_PREFIX" \
        --html "${OUTPUT_PREFIX}.html" \
        --headless
else
    GRPC_TARGET=127.0.0.1:50052 locust -f locustfile_grpc.py \
        -u "$USERS" \
        -r "$SPAWN_RATE" \
        -t "$DURATION" \
        --csv "$OUTPUT_PREFIX" \
        --html "${OUTPUT_PREFIX}.html" \
        --headless
fi

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "OK: ${OUTPUT_PREFIX}_stats.csv ${OUTPUT_PREFIX}_failures.csv ${OUTPUT_PREFIX}_exceptions.csv ${OUTPUT_PREFIX}.html"
else
    echo "FAIL (code=$EXIT_CODE)"
fi

exit $EXIT_CODE

