"""Провайдеры прямых зависимостей: Maven и тестовый режим."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from src.config import AppConfig
from src.maven import MavenError, parse_coordinate
from src.repository import RepositoryError, fetch_direct_dependencies
from src.test_repo import (
    TestRepoError,
    load_test_repo,
    make_test_getter,
)


class ProviderError(Exception):
    """Ошибка получения зависимостей."""


def make_dependency_getter(
    config: AppConfig,
) -> Callable[[str], list[str]]:
    """Создать функцию прямых зависимостей по конфигурации."""
    if config.test_mode:
        return _make_test_mode_getter(config)
    return _make_maven_getter(config.repository)


def _make_test_mode_getter(
    config: AppConfig,
) -> Callable[[str], list[str]]:
    path = Path(config.repository)
    try:
        repo = load_test_repo(path)
        return make_test_getter(repo)
    except TestRepoError as exc:
        raise ProviderError(str(exc)) from exc


def _make_maven_getter(
    repository: str,
) -> Callable[[str], list[str]]:
    def get_deps(package_id: str) -> list[str]:
        try:
            parse_coordinate(package_id)
            deps = fetch_direct_dependencies(
                package_id,
                repository,
            )
        except (MavenError, RepositoryError) as exc:
            raise ProviderError(str(exc)) from exc
        return [dep.format() for dep in deps]

    return get_deps
