# Dependency Graph CLI

## 1. Общее описание

Инструмент визуализации графа зависимостей для менеджера пакетов
Maven (вариант №4). Готовые менеджеры пакетов и сторонние библиотеки
для получения зависимостей не используются.

Реализован этап 1: минимальный CLI-прототип с конфигурацией из
INI-файла, вывод параметров и обработка ошибок.

Язык реализации: Python 3 (стандартная библиотека).

## 2. Функции и настройки

### Модули

| Файл | Назначение |
|------|------------|
| `src/main.py` | Точка входа CLI, вывод параметров |
| `src/config.py` | Чтение и проверка INI-конфигурации |

### Параметры INI (`[app]`)

| Ключ | Описание |
|------|----------|
| `package_name` | Имя анализируемого пакета |
| `repository` | URL репозитория или путь к тестовому файлу |
| `test_mode` | Режим тестового репозитория (`true`/`false`) |
| `output_image` | Имя файла с изображением графа |
| `ascii_tree` | Вывод зависимостей ASCII-деревом |
| `max_depth` | Максимальная глубина анализа (>= 0) |

### Описание функций (этап 1)

#### `src/config.py`

| Имя | Назначение |
|-----|------------|
| `AppConfig` | Неизменяемая структура параметров. |
| `AppConfig.format_dump()` | Текст `ключ=значение` по строкам. |
| `load_config(path)` | Загрузка INI; при ошибке — `ConfigError`. |
| `ConfigError` | Исключение ошибок конфигурации. |

#### `src/main.py`

| Имя | Назначение |
|-----|------------|
| `parse_cli_args(argv)` | Разбор `--config PATH`. |
| `run(argv)` | Загрузка конфига, вывод параметров, код выхода. |
| `main()` | Точка входа модуля. |

### Аргументы командной строки

| Параметр | Описание |
|----------|----------|
| `--config PATH` | Путь к INI-файлу (обязателен) |

При успешном запуске на stdout печатаются все параметры в формате
`ключ=значение`. Ошибки конфигурации — в stderr, код выхода 1.

## 3. Сборка и запуск

Сборка не требуется.

### Запуск

```bash
./run.sh
```

```bash
python3 -m src.main --config examples/config.ok.ini
```

### Скрипты проверки (этап 1)

```bash
chmod +x run.sh scripts/*.sh
./scripts/test_ok.sh
./scripts/test_test_mode.sh
./scripts/test_errors.sh
```

### Тесты

```bash
python3 -m unittest discover -s tests -v
```

## 4. Примеры использования

Успешный запуск:

```
package_name=org.apache.commons:commons-lang3:3.14.0
repository=https://repo.maven.apache.org/maven2
test_mode=false
output_image=graph.png
ascii_tree=true
max_depth=3
```

Ошибки:

```
config: examples/no-such.ini: no such file
config: ...: missing key 'max_depth'
config: 'max_depth' must be >= 0, got -1
config: 'test_mode' must be boolean, got 'maybe'
config: 'package_name' must not be empty
config: ...: missing section [app]
```
