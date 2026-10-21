"""Точка входа CLI: загрузка конфигурации и вывод параметров."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.config import ConfigError, load_config

_EXIT_OK = 0
_EXIT_ERROR = 1


def parse_cli_args(argv: list[str] | None = None) -> Path:
    """Разобрать аргументы командной строки приложения."""
    parser = argparse.ArgumentParser(
        description="Maven dependency graph visualizer",
    )
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to INI configuration file",
    )
    ns = parser.parse_args(argv)
    return ns.config


def run(argv: list[str] | None = None) -> int:
    """Запустить приложение. Возвращает код выхода."""
    config_path = parse_cli_args(argv)
    try:
        config = load_config(config_path)
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        return _EXIT_ERROR
    print(config.format_dump())
    return _EXIT_OK


def main() -> None:
    """Точка входа модуля."""
    raise SystemExit(run())


if __name__ == "__main__":
    main()
