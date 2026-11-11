"""Проверки обратных зависимостей и обхода BFS."""

import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from src.main import run

from src.graph import build_graph_bfs
from src.reverse import reverse_getter
from src.test_repo import TestRepoError


class TestReverse(unittest.TestCase):
    def test_shared_dependency_and_depth(self) -> None:
        repo = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        graph = build_graph_bfs("D", 2, reverse_getter(repo, "D"))
        self.assertEqual(graph.edges["D"], ["B", "C"])
        self.assertEqual(graph.edges["B"], ["A"])
        self.assertEqual(graph.edges["C"], ["A"])

    def test_cycle_and_depth(self) -> None:
        repo = {"A": ["B"], "B": ["C"], "C": ["A"]}
        graph = build_graph_bfs("A", 1, reverse_getter(repo, "A"))
        self.assertEqual(graph.edges, {"A": ["C"], "C": []})
        graph = build_graph_bfs("A", 5, reverse_getter(repo, "A"))
        self.assertEqual(graph.edges["B"], ["A"])

    def test_unknown_and_leaf(self) -> None:
        getter = reverse_getter({"A": ["B"]}, "B")
        self.assertEqual(getter("B"), ["A"])
        self.assertEqual(getter("A"), [])
        with self.assertRaises(TestRepoError):
            reverse_getter({"A": []}, "Z")


class TestReverseCli(unittest.TestCase):
    def test_reverse_example(self) -> None:
        root = Path(__file__).resolve().parent.parent
        config = root / "examples" / "config.reverse_simple.ini"
        output = StringIO()
        with redirect_stdout(output):
            code = run(["--config", str(config), "--reverse"])
        self.assertEqual(code, 0)
        self.assertIn("D -> B", output.getvalue())
        self.assertIn("D -> C", output.getvalue())

    def test_maven_reverse_reports_error(self) -> None:
        root = Path(__file__).resolve().parent.parent
        config = root / "examples" / "config.ok.ini"
        output = StringIO()
        with redirect_stderr(output):
            code = run(["--config", str(config), "--reverse"])
        self.assertEqual(code, 1)
        self.assertIn("requires test_mode=true", output.getvalue())
