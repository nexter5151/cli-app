"""Обратные зависимости тестового репозитория."""

from collections.abc import Callable

from src.test_repo import TestRepoError


def reverse_getter(
    repo: dict[str, list[str]],
    root: str,
) -> Callable[[str], list[str]]:
    """Создать источник обратных рёбер для обхода BFS."""
    reverse: dict[str, list[str]] = {name: [] for name in repo}
    for package, dependencies in repo.items():
        for dependency in dependencies:
            reverse.setdefault(dependency, []).append(package)
    if root not in reverse:
        raise TestRepoError(f"test repo: unknown package {root!r}")

    def get_dependents(package: str) -> list[str]:
        return reverse.get(package, [])

    return get_dependents
