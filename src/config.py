"""Чтение и проверка конфигурации из INI-файла."""

from __future__ import annotations

import configparser
from dataclasses import dataclass
from pathlib import Path

_CONFIG_SECTION = "app"
_MIN_DEPTH = 0
_TRUE_VALUES = frozenset({"true", "yes", "1", "on"})
_FALSE_VALUES = frozenset({"false", "no", "0", "off"})

_REQUIRED_KEYS = (
    "package_name",
    "repository",
    "test_mode",
    "output_image",
    "ascii_tree",
    "max_depth",
)


@dataclass(frozen=True)
class AppConfig:
    """Параметры приложения, задаваемые пользователем."""

    package_name: str
    repository: str
    test_mode: bool
    output_image: str
    ascii_tree: bool
    max_depth: int

    def as_key_values(self) -> list[tuple[str, str]]:
        """Все параметры в виде пар ключ–значение."""
        return [
            ("package_name", self.package_name),
            ("repository", self.repository),
            ("test_mode", _bool_text(self.test_mode)),
            ("output_image", self.output_image),
            ("ascii_tree", _bool_text(self.ascii_tree)),
            ("max_depth", str(self.max_depth)),
        ]

    def format_dump(self) -> str:
        """Текст параметров в формате ключ=значение."""
        return "\n".join(
            f"{key}={value}" for key, value in self.as_key_values()
        )


class ConfigError(Exception):
    """Ошибка загрузки или проверки конфигурации."""


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def load_config(path: Path) -> AppConfig:
    """Загрузить и проверить INI-конфигурацию.

    Raises:
        ConfigError: файл отсутствует, формат неверен или поля невалидны.
    """
    if not path.is_file():
        raise ConfigError(f"config: {path}: no such file")
    parser = configparser.ConfigParser()
    try:
        read_ok = parser.read(path, encoding="utf-8")
    except configparser.Error as exc:
        raise ConfigError(f"config: {path}: invalid INI: {exc}") from exc
    if not read_ok:
        raise ConfigError(f"config: {path}: cannot read file")
    if not parser.has_section(_CONFIG_SECTION):
        raise ConfigError(
            f"config: {path}: missing section [{_CONFIG_SECTION}]"
        )
    section = parser[_CONFIG_SECTION]
    values = _require_keys(section, path)
    return AppConfig(
        package_name=_nonempty(values["package_name"], "package_name"),
        repository=_nonempty(values["repository"], "repository"),
        test_mode=_parse_bool(values["test_mode"], "test_mode"),
        output_image=_nonempty(values["output_image"], "output_image"),
        ascii_tree=_parse_bool(values["ascii_tree"], "ascii_tree"),
        max_depth=_parse_depth(values["max_depth"]),
    )


def _require_keys(
    section: configparser.SectionProxy,
    path: Path,
) -> dict[str, str]:
    values: dict[str, str] = {}
    for key in _REQUIRED_KEYS:
        if key not in section or section.get(key) is None:
            raise ConfigError(
                f"config: {path}: missing key '{key}'"
            )
        values[key] = section.get(key, raw=True).strip()
    return values


def _nonempty(value: str, key: str) -> str:
    if not value:
        raise ConfigError(f"config: '{key}' must not be empty")
    return value


def _parse_bool(value: str, key: str) -> bool:
    lowered = value.lower()
    if lowered in _TRUE_VALUES:
        return True
    if lowered in _FALSE_VALUES:
        return False
    raise ConfigError(
        f"config: '{key}' must be boolean, got {value!r}"
    )


def _parse_depth(value: str) -> int:
    try:
        depth = int(value)
    except ValueError as exc:
        raise ConfigError(
            f"config: 'max_depth' must be an integer, got {value!r}"
        ) from exc
    if depth < _MIN_DEPTH:
        raise ConfigError(
            f"config: 'max_depth' must be >= {_MIN_DEPTH}, got {depth}"
        )
    return depth
