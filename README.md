# Dependency Graph CLI

## 1. Общее описание

Инструмент визуализации графа зависимостей для менеджера пакетов
Maven (вариант №4). Готовые менеджеры пакетов и сторонние библиотеки
для получения зависимостей не используются.

Реализованы этапы 1–2: CLI с INI-конфигурацией и сбор прямых
зависимостей пакета из Maven-репозитория по HTTP (stdlib).

Язык реализации: Python 3 (стандартная библиотека).

## 2. Функции и настройки

### Модули

| Файл | Назначение |
|------|------------|
| `src/main.py` | Точка входа CLI |
| `src/config.py` | Чтение и проверка INI-конфигурации |
| `src/maven.py` | Координаты GAV и разбор POM |
| `src/repository.py` | Загрузка POM по URL репозитория |

### Параметры INI (`[app]`)

| Ключ | Описание |
|------|----------|
| `package_name` | Пакет `groupId:artifactId:version` |
| `repository` | URL Maven-репозитория или путь (этап 3) |
| `test_mode` | Режим тестового репозитория |
| `output_image` | Имя файла с изображением графа |
| `ascii_tree` | Вывод зависимостей ASCII-деревом |
| `max_depth` | Максимальная глубина анализа (>= 0) |

### Описание функций (этап 2)

#### `src/maven.py`

| Имя | Назначение |
|-----|------------|
| `MavenCoordinate` | GAV-координаты пакета. |
| `parse_coordinate(text)` | Разбор `group:artifact:version`. |
| `parse_pom_dependencies(text)` | Прямые зависимости из POM XML. |

#### `src/repository.py`

| Имя | Назначение |
|-----|------------|
| `build_pom_url(repo, coord)` | URL `.../artifact-version.pom`. |
| `fetch_pom_text(url)` | HTTP-загрузка POM. |
| `fetch_direct_dependencies(...)` | Координаты → список зависимостей. |

### Аргументы командной строки

| Параметр | Описание |
|----------|----------|
| `--config PATH` | Путь к INI-файлу (обязателен) |

На этапе 2 при успешном запуске на stdout печатаются прямые
зависимости (`groupId:artifactId:version`), по одной на строку.
Ошибки — в stderr, код выхода 1.

## 3. Сборка и запуск

Сборка не требуется. Нужен доступ в сеть к Maven-репозиторию.

### Запуск

```bash
./run.sh
```

```bash
python3 -m src.main --config examples/config.ok.ini
```

### Скрипты проверки

```bash
chmod +x run.sh scripts/*.sh
./scripts/test_ok.sh
./scripts/test_test_mode.sh
./scripts/test_errors.sh
./scripts/test_stage2.sh
./scripts/test_stage2_missing.sh
```

### Тесты

```bash
python3 -m unittest discover -s tests -v
```

## 4. Примеры использования

Прямые зависимости `junit:junit:4.13.2`:

```
org.hamcrest:hamcrest-core:1.3
```

Ошибки:

```
config: 'max_depth' must be >= 0, got -1
package_name must be groupId:artifactId:version, ...
repository: HTTP 404 for https://...
```
