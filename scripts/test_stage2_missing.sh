#!/usr/bin/env bash
# Этап 2: ошибка — пакет не найден в репозитории.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo ">>> python3 -m src.main --config examples/config.missing_pkg.ini"
set +e
python3 -m src.main --config examples/config.missing_pkg.ini
code=$?
set -e
echo "exit_code=${code}"
