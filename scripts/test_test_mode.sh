#!/usr/bin/env bash
# Конфигурация с режимом тестового репозитория.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo ">>> python3 -m src.main --config examples/config.test_mode.ini"
exec python3 -m src.main --config examples/config.test_mode.ini
