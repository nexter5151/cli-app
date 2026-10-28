#!/usr/bin/env bash
# Этап 3: ограничение max_depth на цепочке.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo ">>> python3 -m src.main --config examples/config.test_deep.ini"
exec python3 -m src.main --config examples/config.test_deep.ini
