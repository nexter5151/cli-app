"""Представления графа Graphviz и ASCII."""

import json
import subprocess
from pathlib import Path

from src.graph import DependencyGraph


class VisualizationError(Exception):
    """Ошибка создания изображения."""


def format_dot(graph: DependencyGraph) -> str:
    """Построить описание Graphviz с сохранением отдельных узлов."""
    nodes = {graph.root, *graph.edges}
    for children in graph.edges.values():
        nodes.update(children)
    lines = ["digraph dependencies {"]
    lines.extend(f"  {json.dumps(node)};" for node in sorted(nodes))
    for source, children in sorted(graph.edges.items()):
        for child in children:
            lines.append(f"  {json.dumps(source)} -> {json.dumps(child)};")
    return "\n".join([*lines, "}"])


def save_png(graph: DependencyGraph, path: str) -> None:
    """Сохранить граф в PNG с помощью программы dot."""
    try:
        subprocess.run(
            ["dot", "-Tpng", "-o", str(Path(path))],
            input=format_dot(graph), text=True, check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise VisualizationError(f"graphviz: {exc}") from exc


def format_ascii(graph: DependencyGraph) -> str:
    """Показать дерево без бесконечного обхода циклов."""
    lines = []
    seen: set[str] = set()
    stack = [(graph.root, "", "", "")]
    while stack:
        node, prefix, branch, continuation = stack.pop()
        repeated = node in seen
        lines.append(prefix + branch + node + (" (*)" if repeated else ""))
        if repeated:
            continue
        seen.add(node)
        children = graph.edges.get(node, [])
        child_prefix = prefix + continuation
        for index in reversed(range(len(children))):
            last = index == len(children) - 1
            child_branch = "`-- " if last else "|-- "
            child_continuation = "    " if last else "|   "
            stack.append((children[index], child_prefix, child_branch,
                          child_continuation))
    return "\n".join(lines)
