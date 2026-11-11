#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
if [[ $# -eq 0 ]]; then
  exec python3 -m src.main --config examples/config.test_mode.ini
fi
exec python3 -m src.main "$@"
