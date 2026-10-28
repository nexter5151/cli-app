"""Построение графа зависимостей алгоритмом BFS."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field

GetDeps = Callable[[str], list[str]]


@dataclass
class DependencyGraph:
    """Граф зависимостей: корень и список рёбер."""

    root: str
    edges: dict[str, list[str]] = field(default_factory=dict)

    def format_edges(self) -> str:
        """Текстовое представление рёбер графа."""
        lines: list[str] = []
        for source in sorted(self.edges.keys()):
            targets = self.edges[source]
            if not targets:
                lines.append(f"{source}")
                continue
            for target in targets:
                lines.append(f"{source} -> {target}")
        return "\n".join(lines)


def build_graph_bfs(
    root: str,
    max_depth: int,
    get_deps: GetDeps,
) -> DependencyGraph:
    """Построить граф BFS без рекурсии с учётом глубины и циклов."""
    graph = DependencyGraph(root=root)
    visited: set[str] = {root}
    queue: deque[tuple[str, int]] = deque([(root, 0)])
    while queue:
        current, depth = queue.popleft()
        if depth >= max_depth:
            graph.edges.setdefault(current, [])
            continue
        children = get_deps(current)
        graph.edges[current] = list(children)
        for child in children:
            if child in visited:
                continue
            visited.add(child)
            queue.append((child, depth + 1))
    return graph
