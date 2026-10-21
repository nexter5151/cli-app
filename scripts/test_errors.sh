#!/usr/bin/env bash
# Демонстрация ошибок для всех проверяемых параметров.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

run_case() {
  local label="$1"
  local file="$2"
  echo "=== ${label} ==="
  set +e
  python3 -m src.main --config "${file}"
  echo "exit_code=$?"
  set -e
  echo
}

run_case "missing file" "examples/no-such.ini"
run_case "missing key" "examples/config.missing_key.ini"
run_case "bad max_depth" "examples/config.bad_depth.ini"
run_case "bad boolean" "examples/config.bad_bool.ini"
run_case "empty package_name" "examples/config.empty_package.ini"
run_case "missing section" "examples/config.no_section.ini"
