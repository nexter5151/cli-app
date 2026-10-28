"""Тестовый репозиторий: файл с пакетами A–Z."""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

_PACKAGE_NAME = re.compile(r"^[A-Z]+$")


class TestRepoError(Exception):
    """Ошибка загрузки или чтения тестового репозитория."""


def load_test_repo(path: Path) -> dict[str, list[str]]:
    """Загрузить граф из файла.

    Формат строки: ``A B C`` — пакет A зависит от B и C.
    Пустые строки и строки с ``#`` игнорируются.
    """
    if not path.is_file():
        raise TestRepoError(f"test repo: {path}: no such file")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise TestRepoError(f"test repo: {path}: {exc}") from exc
    graph: dict[str, list[str]] = {}
    for line_no, raw in enumerate(text.splitlines(), start=1):
        _parse_repo_line(raw, line_no, graph)
    return graph


def _parse_repo_line(
    raw: str,
    line_no: int,
    graph: dict[str, list[str]],
) -> None:
    line = raw.strip()
    if not line or line.startswith("#"):
        return
    parts = line.split()
    package = parts[0]
    deps = parts[1:]
    _validate_name(package, line_no)
    for dep in deps:
        _validate_name(dep, line_no)
    if package in graph:
        raise TestRepoError(
            f"test repo: line {line_no}: duplicate package "
            f"{package!r}"
        )
    graph[package] = deps


def _validate_name(name: str, line_no: int) -> None:
    if _PACKAGE_NAME.fullmatch(name) is None:
        raise TestRepoError(
            f"test repo: line {line_no}: invalid package "
            f"name {name!r} (use A-Z)"
        )


def make_test_getter(
    repo: dict[str, list[str]],
) -> Callable[[str], list[str]]:
    """Фабрика get_deps для тестового репозитория."""

    def get_deps(package_id: str) -> list[str]:
        if package_id not in repo:
            raise TestRepoError(
                f"test repo: unknown package {package_id!r}"
            )
        return list(repo[package_id])

    return get_deps
