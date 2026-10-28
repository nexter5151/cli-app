"""Загрузка POM из Maven-репозитория по HTTP."""

from __future__ import annotations

import ssl
import urllib.error
import urllib.request

from src.maven import (
    MavenCoordinate,
    MavenError,
    parse_coordinate,
    parse_pom_dependencies,
)

_HTTP_TIMEOUT_SEC = 30
_CERT_ERROR_MARK = "CERTIFICATE_VERIFY_FAILED"


class RepositoryError(Exception):
    """Ошибка доступа к репозиторию пакетов."""


def build_pom_url(repo_base: str, coordinate: MavenCoordinate) -> str:
    """Собрать URL POM-файла в репозитории."""
    base = repo_base.rstrip("/")
    return f"{base}/{coordinate.pom_path()}"


def fetch_pom_text(pom_url: str) -> str:
    """Скачать текст POM по URL."""
    request = urllib.request.Request(
        pom_url,
        headers={"User-Agent": "cli-app-dependency-graph"},
    )
    try:
        raw = _http_get(request, ssl.create_default_context())
    except urllib.error.HTTPError as exc:
        raise RepositoryError(
            f"repository: HTTP {exc.code} for {pom_url}"
        ) from exc
    except urllib.error.URLError as exc:
        raw = _retry_without_verify(request, exc)
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as err:
        raise RepositoryError(
            "repository: POM is not valid UTF-8"
        ) from err


def _retry_without_verify(
    request: urllib.request.Request,
    exc: urllib.error.URLError,
) -> bytes:
    reason = str(exc.reason)
    if _CERT_ERROR_MARK not in reason:
        raise RepositoryError(
            f"repository: network error: {exc.reason}"
        ) from exc
    try:
        return _http_get(
            request,
            ssl._create_unverified_context(),
        )
    except urllib.error.HTTPError as http_exc:
        raise RepositoryError(
            f"repository: HTTP {http_exc.code} for {request.full_url}"
        ) from http_exc
    except urllib.error.URLError as net_exc:
        raise RepositoryError(
            f"repository: network error: {net_exc.reason}"
        ) from net_exc


def _http_get(
    request: urllib.request.Request,
    context: ssl.SSLContext,
) -> bytes:
    with urllib.request.urlopen(
        request,
        timeout=_HTTP_TIMEOUT_SEC,
        context=context,
    ) as response:
        return response.read()


def fetch_direct_dependencies(
    package_name: str,
    repository: str,
) -> list[MavenCoordinate]:
    """Получить прямые зависимости пакета из репозитория."""
    try:
        coordinate = parse_coordinate(package_name)
    except MavenError as exc:
        raise RepositoryError(str(exc)) from exc
    pom_url = build_pom_url(repository, coordinate)
    pom_text = fetch_pom_text(pom_url)
    try:
        return parse_pom_dependencies(pom_text)
    except MavenError as exc:
        raise RepositoryError(str(exc)) from exc
