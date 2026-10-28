#!/usr/bin/env bash
# Этап 2: прямые зависимости пакета из Maven Central.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo ">>> python3 -m src.main --config examples/config.ok.ini"
exec python3 -m src.main --config examples/config.ok.ini
