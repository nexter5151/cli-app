"""Тесты BFS-графа и тестового репозитория."""

import unittest
from pathlib import Path

from src.graph import build_graph_bfs
from src.test_repo import TestRepoError, load_test_repo, make_test_getter


ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"


class TestTestRepo(unittest.TestCase):
    def test_load_simple(self) -> None:
        repo = load_test_repo(EXAMPLES / "test_repo_simple.txt")
        self.assertEqual(repo["A"], ["B", "C"])
        self.assertEqual(repo["D"], [])

    def test_missing_file(self) -> None:
        with self.assertRaises(TestRepoError):
            load_test_repo(EXAMPLES / "no-repo.txt")

    def test_invalid_name(self) -> None:
        path = EXAMPLES / "bad_names.txt"
        path.write_text("A b\n", encoding="utf-8")
        try:
            with self.assertRaises(TestRepoError):
                load_test_repo(path)
        finally:
            path.unlink()


class TestBfs(unittest.TestCase):
    def test_depth_limit(self) -> None:
        repo = load_test_repo(EXAMPLES / "test_repo_deep.txt")
        getter = make_test_getter(repo)
        graph = build_graph_bfs("A", 2, getter)
        text = graph.format_edges()
        self.assertIn("A -> B", text)
        self.assertIn("B -> C", text)
        self.assertNotIn("C -> D", text)

    def test_cycle(self) -> None:
        repo = load_test_repo(EXAMPLES / "test_repo_cycle.txt")
        getter = make_test_getter(repo)
        graph = build_graph_bfs("A", 5, getter)
        text = graph.format_edges()
        self.assertIn("A -> B", text)
        self.assertIn("B -> C", text)
        self.assertIn("C -> A", text)

    def test_simple_full(self) -> None:
        repo = load_test_repo(EXAMPLES / "test_repo_simple.txt")
        getter = make_test_getter(repo)
        graph = build_graph_bfs("A", 3, getter)
        text = graph.format_edges()
        self.assertIn("A -> B", text)
        self.assertIn("A -> C", text)
        self.assertIn("B -> D", text)
        self.assertIn("C -> D", text)


if __name__ == "__main__":
    unittest.main()
