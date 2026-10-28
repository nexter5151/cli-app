#!/usr/bin/env bash
# Этап 3: тестовый репозиторий с циклом.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo ">>> python3 -m src.main --config examples/config.test_cycle.ini"
exec python3 -m src.main --config examples/config.test_cycle.ini
