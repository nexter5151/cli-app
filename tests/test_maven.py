"""Тесты координат Maven и разбора POM."""

import unittest
from pathlib import Path

from src.maven import (
    MavenError,
    parse_coordinate,
    parse_pom_dependencies,
)
from src.repository import build_pom_url


ROOT = Path(__file__).resolve().parent.parent
SAMPLE_POM = ROOT / "examples" / "sample.pom.xml"


class TestCoordinate(unittest.TestCase):
    def test_parse_ok(self) -> None:
        coord = parse_coordinate(
            "org.apache.commons:commons-lang3:3.14.0"
        )
        self.assertEqual(coord.group_id, "org.apache.commons")
        self.assertEqual(coord.artifact_id, "commons-lang3")
        self.assertEqual(coord.version, "3.14.0")

    def test_parse_bad(self) -> None:
        with self.assertRaises(MavenError):
            parse_coordinate("only-two:parts")

    def test_pom_path(self) -> None:
        coord = parse_coordinate("org.foo:bar:1.2.3")
        self.assertEqual(
            coord.pom_path(),
            "org/foo/bar/1.2.3/bar-1.2.3.pom",
        )


class TestPomParse(unittest.TestCase):
    def test_sample_pom(self) -> None:
        text = SAMPLE_POM.read_text(encoding="utf-8")
        deps = parse_pom_dependencies(text)
        formatted = [d.format() for d in deps]
        self.assertIn(
            "org.apache.commons:commons-lang3:3.14.0",
            formatted,
        )
        self.assertIn("junit:junit:4.13.2", formatted)

    def test_empty_dependencies(self) -> None:
        pom = (
            "<project>"
            "<dependencies></dependencies>"
            "</project>"
        )
        self.assertEqual(parse_pom_dependencies(pom), [])

    def test_property_resolution(self) -> None:
        text = SAMPLE_POM.read_text(encoding="utf-8")
        deps = parse_pom_dependencies(text)
        versions = {d.artifact_id: d.version for d in deps}
        self.assertEqual(versions["commons-lang3"], "3.14.0")


class TestPomUrl(unittest.TestCase):
    def test_build_url(self) -> None:
        coord = parse_coordinate("org.foo:bar:1.0")
        url = build_pom_url(
            "https://repo.example.com/maven2/",
            coord,
        )
        self.assertEqual(
            url,
            "https://repo.example.com/maven2/"
            "org/foo/bar/1.0/bar-1.0.pom",
        )


if __name__ == "__main__":
    unittest.main()
