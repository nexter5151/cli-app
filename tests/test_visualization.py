"""Проверка визуализации зависимостей."""

import tempfile
import unittest
from pathlib import Path

from src.graph import DependencyGraph
from src.visualization import format_ascii, format_dot, save_png


class TestVisualization(unittest.TestCase):
    def test_cycle_and_escaping(self) -> None:
        graph = DependencyGraph('A', {'A': ['B'], 'B': ['A']})
        self.assertIn('"B" -> "A"', format_dot(graph))
        self.assertIn('A (*)', format_ascii(graph))

    def test_png(self) -> None:
        graph = DependencyGraph('A', {'A': ['B']})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'graph.png'
            save_png(graph, str(path))
            self.assertTrue(path.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'))
