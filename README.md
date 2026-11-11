# Dependency Graph CLI

## 1. Общее описание

Инструмент визуализации графа зависимостей для менеджера пакетов
Maven (вариант №4). Готовые менеджеры пакетов и сторонние библиотеки
для получения зависимостей не используются.

Реализованы этапы 1–3: INI-конфигурация, сбор зависимостей из Maven
POM и построение транзитивного графа алгоритмом BFS (с тестовым
режимом).

Язык реализации: Python 3 (стандартная библиотека).

## 2. Функции и настройки

### Модули

| Файл | Назначение |
|------|------------|
| `src/main.py` | Точка входа CLI |
| `src/config.py` | Чтение и проверка INI-конфигурации |
| `src/maven.py` | Координаты GAV и разбор POM |
| `src/repository.py` | Загрузка POM по URL |
| `src/graph.py` | BFS-граф зависимостей |
| `src/test_repo.py` | Тестовый репозиторий из файла |
| `src/providers.py` | Выбор источника зависимостей |

### Параметры INI (`[app]`)

| Ключ | Описание |
|------|----------|
| `package_name` | Пакет GAV или имя `A`–`Z` в test_mode |
| `repository` | URL Maven или путь к файлу тестового графа |
| `test_mode` | `true` — читать граф из файла |
| `output_image` | Имя файла изображения (этап 5) |
| `ascii_tree` | ASCII-дерево (этап 5) |
| `max_depth` | Максимальная глубина BFS (>= 0) |

### Тестовый репозиторий

Строка `A B C` означает: пакет `A` зависит от `B` и `C`.
Имена — заглавные латинские буквы. Примеры:
`examples/test_repo_simple.txt`, `test_repo_cycle.txt`,
`test_repo_deep.txt`.

### Описание функций (этап 3)

| Имя | Назначение |
|-----|------------|
| `build_graph_bfs(root, depth, get_deps)` | BFS без рекурсии, циклы и глубина. |
| `DependencyGraph.format_edges()` | Текст рёбер `A -> B`. |
| `load_test_repo(path)` | Загрузка тестового файла графа. |
| `make_dependency_getter(config)` | Maven или test_mode. |

### Аргументы командной строки

| Параметр | Описание |
|----------|----------|
| `--config PATH` | Путь к INI-файлу (обязателен) |

На этапе 3 на stdout печатается граф рёбер. Ошибки — stderr, код 1.

## 3. Сборка и запуск

```bash
./run.sh
python3 -m src.main --config examples/config.test_mode.ini
```

### Скрипты проверки

```bash
chmod +x run.sh scripts/*.sh
./scripts/test_ok.sh
./scripts/test_errors.sh
./scripts/test_stage2.sh
./scripts/test_stage3_simple.sh
./scripts/test_stage3_cycle.sh
./scripts/test_stage3_deep.sh
```

### Тесты

```bash
python3 -m unittest discover -s tests -v
```

## 4. Примеры использования

Тестовый режим (`max_depth=2`):

```
A -> B
A -> C
B -> D
C -> D
D
```

Цикл:

```
A -> B
B -> C
C -> A
```

Ограничение глубины на цепочке A→B→C→D→E при `max_depth=2`:

```
A -> B
B -> C
C
```

### Этап 4: обратные зависимости

Флаг `--reverse` показывает пакеты, зависящие от `package_name`.
Поиск доступен в тестовом режиме: весь файл репозитория используется
для построения обратных рёбер, затем выполняется BFS с `max_depth`.
Например, `D -> B` означает, что пакет B зависит от D.
Циклы не приводят к бесконечному обходу.

```bash
python3 -m src.main --config examples/config.reverse_simple.ini --reverse
python3 -m src.main --config examples/config.reverse_cycle.ini --reverse
python3 -m src.main --config examples/config.reverse_deep.ini --reverse
```

В Maven-режиме поиск обратных зависимостей не реализован: Maven POM
содержит прямые зависимости и не предоставляет полного списка пакетов,
которые зависят от заданного.

Под каждым ребром выводится требование версии из координат зависимости.
Диапазоны показываются как записаны в POM; если версия неизвестна или
используется тестовый репозиторий, выводится `not specified`. Выбор
конкретной версии из диапазона и обработка наследования Maven не реализованы.

### Этап 5: визуализация

Для создания PNG необходим установленный Graphviz (`dot` в PATH).
Программа создаёт изображение по пути `output_image` из INI. Если
`ascii_tree = true`, дерево выводится в консоль; `(*)` означает повторный
узел. Функция `format_dot` возвращает текст Graphviz.

Примеры трёх графов: `config.test_mode.ini`, `config.test_cycle.ini`,
`config.test_deep.ini`. Измените `ascii_tree` на `true` для вывода дерева.
Сравнение с Maven (`maven-dependency-plugin:3.8.1:tree`, `-Dverbose`)
проведено для отдельных проектов с одной зависимостью, глубина CLI — 3:

- `junit:junit:4.13.2`: Maven показывает `hamcrest-core:1.3`;
  CLI дополнительно показывает `hamcrest-library:1.3` и его зависимость
  `hamcrest-core:1.3`. В POM JUnit для `hamcrest-library` указан
  `scope=test`: Maven не включает его как транзитивную зависимость,
  тогда как CLI пока не фильтрует scope.
- `org.hamcrest:hamcrest-core:1.3`: оба вывода не содержат детей.
- `org.hamcrest:hamcrest-library:1.3`: оба вывода показывают прямую
  зависимость `hamcrest-core:1.3`.

Maven также учитывает наследование POM, управление версиями и разрешение
конфликтов; их поддержка в CLI неполная. При сравнении Maven показывает
корень временного проекта и добавленные поля `jar` и `scope`.
