"""Координаты Maven-пакетов и разбор POM."""

from __future__ import annotations

import re
import xml.etree.ElementTree as element_tree
from dataclasses import dataclass

_GAV_PARTS = 3
_MAX_RESOLVE_PASSES = 5
_PROP_PATTERN = re.compile(r"\$\{([^}]+)\}")


class MavenError(Exception):
    """Ошибка разбора координат или POM."""


@dataclass(frozen=True)
class MavenCoordinate:
    """Координаты Maven: groupId:artifactId:version."""

    group_id: str
    artifact_id: str
    version: str

    def format(self) -> str:
        """Строка groupId:artifactId:version."""
        return f"{self.group_id}:{self.artifact_id}:{self.version}"

    def pom_path(self) -> str:
        """Относительный путь к POM в Maven-репозитории."""
        group_path = self.group_id.replace(".", "/")
        name = f"{self.artifact_id}-{self.version}.pom"
        return (
            f"{group_path}/{self.artifact_id}/"
            f"{self.version}/{name}"
        )


def parse_coordinate(text: str) -> MavenCoordinate:
    """Разобрать package_name вида group:artifact:version."""
    parts = [p.strip() for p in text.split(":")]
    if len(parts) != _GAV_PARTS:
        raise MavenError(
            "package_name must be groupId:artifactId:version, "
            f"got {text!r}"
        )
    group_id, artifact_id, version = parts
    if not group_id or not artifact_id or not version:
        raise MavenError(
            "package_name parts must not be empty, "
            f"got {text!r}"
        )
    return MavenCoordinate(group_id, artifact_id, version)


def parse_pom_dependencies(pom_text: str) -> list[MavenCoordinate]:
    """Извлечь прямые зависимости из текста POM."""
    try:
        root = element_tree.fromstring(pom_text)
    except element_tree.ParseError as exc:
        raise MavenError(f"invalid POM XML: {exc}") from exc
    props = _read_properties(root)
    deps_node = _find_child(root, "dependencies")
    if deps_node is None:
        return []
    result: list[MavenCoordinate] = []
    for dep in deps_node:
        if _local_tag(dep.tag) != "dependency":
            continue
        coord = _dependency_coordinate(dep, props)
        if coord is not None:
            result.append(coord)
    return result


def _local_tag(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag


def _find_child(
    parent: element_tree.Element,
    name: str,
) -> element_tree.Element | None:
    for child in parent:
        if _local_tag(child.tag) == name:
            return child
    return None


def _child_text(parent: element_tree.Element, name: str) -> str:
    node = _find_child(parent, name)
    if node is None or node.text is None:
        return ""
    return node.text.strip()


def _read_properties(
    root: element_tree.Element,
) -> dict[str, str]:
    props: dict[str, str] = {}
    for key in ("groupId", "artifactId", "version"):
        value = _child_text(root, key)
        if value:
            props[f"project.{key}"] = value
            props[f"pom.{key}"] = value
    props_node = _find_child(root, "properties")
    if props_node is None:
        return props
    for child in props_node:
        name = _local_tag(child.tag)
        text = (child.text or "").strip()
        if name and text:
            props[name] = text
    return props


def _resolve(text: str, props: dict[str, str]) -> str:
    current = text
    for _ in range(_MAX_RESOLVE_PASSES):
        updated = _PROP_PATTERN.sub(
            lambda match: props.get(match.group(1), match.group(0)),
            current,
        )
        if updated == current:
            break
        current = updated
    return current


def _dependency_coordinate(
    dep: element_tree.Element,
    props: dict[str, str],
) -> MavenCoordinate | None:
    group_id = _resolve(_child_text(dep, "groupId"), props)
    artifact_id = _resolve(_child_text(dep, "artifactId"), props)
    version = _resolve(_child_text(dep, "version"), props)
    if not group_id or not artifact_id:
        return None
    if not version:
        version = "unknown"
    return MavenCoordinate(group_id, artifact_id, version)
