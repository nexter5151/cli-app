"""Точка входа CLI: граф зависимостей (BFS)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.config import ConfigError, load_config
from src.graph import build_graph_bfs
from src.providers import ProviderError, make_dependency_getter
from src.reverse import reverse_getter
from src.test_repo import TestRepoError, load_test_repo

_EXIT_OK = 0
_EXIT_ERROR = 1


def parse_cli_args(argv: list[str] | None = None) -> argparse.Namespace:
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
    parser.add_argument(
        "--reverse", action="store_true",
        help="Show reverse dependencies from the test repository",
    )
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    """Запустить приложение. Возвращает код выхода."""
    args = parse_cli_args(argv)
    try:
        config = load_config(args.config)
        if args.reverse:
            if not config.test_mode:
                raise ProviderError("reverse mode requires test_mode=true")
            repo = load_test_repo(Path(config.repository))
            get_deps = reverse_getter(repo, config.package_name)
        else:
            get_deps = make_dependency_getter(config)
        graph = build_graph_bfs(
            config.package_name,
            config.max_depth,
            get_deps,
        )
    except (ConfigError, ProviderError, TestRepoError) as exc:
        print(str(exc), file=sys.stderr)
        return _EXIT_ERROR
    text = graph.format_edges()
    if text:
        print(text)
    else:
        print(graph.root)
    return _EXIT_OK


def main() -> None:
    """Точка входа модуля."""
    raise SystemExit(run())


if __name__ == "__main__":
    main()
