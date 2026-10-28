"""Тесты загрузки INI-конфигурации и обработки ошибок."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.config import ConfigError, load_config
from src.graph import DependencyGraph
from src.main import run


ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"


class TestLoadOk(unittest.TestCase):
    def test_ok_config(self) -> None:
        cfg = load_config(EXAMPLES / "config.ok.ini")
        self.assertEqual(cfg.package_name, "junit:junit:4.13.2")
        self.assertFalse(cfg.test_mode)
        self.assertTrue(cfg.ascii_tree)
        self.assertEqual(cfg.max_depth, 3)
        self.assertEqual(cfg.output_image, "graph.png")

    def test_test_mode_config(self) -> None:
        cfg = load_config(EXAMPLES / "config.test_mode.ini")
        self.assertTrue(cfg.test_mode)
        self.assertFalse(cfg.ascii_tree)
        self.assertEqual(cfg.package_name, "A")

    def test_format_dump(self) -> None:
        cfg = load_config(EXAMPLES / "config.ok.ini")
        text = cfg.format_dump()
        self.assertIn("package_name=", text)
        self.assertIn("max_depth=3", text)
        self.assertIn("test_mode=false", text)


class TestLoadErrors(unittest.TestCase):
    def test_missing_file(self) -> None:
        with self.assertRaises(ConfigError) as ctx:
            load_config(EXAMPLES / "no-such.ini")
        self.assertIn("no such file", str(ctx.exception))

    def test_missing_key(self) -> None:
        with self.assertRaises(ConfigError) as ctx:
            load_config(EXAMPLES / "config.missing_key.ini")
        self.assertIn("missing key", str(ctx.exception))

    def test_bad_depth(self) -> None:
        with self.assertRaises(ConfigError) as ctx:
            load_config(EXAMPLES / "config.bad_depth.ini")
        self.assertIn("max_depth", str(ctx.exception))

    def test_bad_bool(self) -> None:
        with self.assertRaises(ConfigError) as ctx:
            load_config(EXAMPLES / "config.bad_bool.ini")
        self.assertIn("boolean", str(ctx.exception))

    def test_empty_package(self) -> None:
        with self.assertRaises(ConfigError) as ctx:
            load_config(EXAMPLES / "config.empty_package.ini")
        self.assertIn("package_name", str(ctx.exception))

    def test_no_section(self) -> None:
        with self.assertRaises(ConfigError) as ctx:
            load_config(EXAMPLES / "config.no_section.ini")
        self.assertIn("missing section", str(ctx.exception))

    def test_invalid_ini(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".ini",
            delete=False,
        ) as handle:
            handle.write("[app\npackage_name = x\n")
            path = Path(handle.name)
        try:
            with self.assertRaises(ConfigError) as ctx:
                load_config(path)
            self.assertIn("invalid INI", str(ctx.exception))
        finally:
            path.unlink()


class TestRun(unittest.TestCase):
    @patch("src.main.build_graph_bfs")
    @patch("src.main.make_dependency_getter")
    def test_run_ok(self, mock_getter, mock_bfs) -> None:
        mock_getter.return_value = lambda _pkg: []
        mock_bfs.return_value = DependencyGraph(
            root="A",
            edges={"A": ["B"], "B": []},
        )
        code = run(
            ["--config", str(EXAMPLES / "config.test_mode.ini")]
        )
        self.assertEqual(code, 0)

    def test_run_error(self) -> None:
        code = run(
            ["--config", str(EXAMPLES / "config.bad_depth.ini")]
        )
        self.assertEqual(code, 1)

    def test_run_test_mode_live(self) -> None:
        code = run(
            ["--config", str(EXAMPLES / "config.test_mode.ini")]
        )
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
