# TASKS.md - План реализации go_computer_use_mcp_server

## Описание проекта
MCP сервер на Go для управления компьютером с использованием библиотеки [robotgo](https://github.com/hightemp/robotgo).

## Архитектура
- Монолитная структура (main.go) по аналогии с примером go_mcp_server_github_api
- Транспорты: SSE и Stdio
- Использование библиотеки `github.com/mark3labs/mcp-go`

---

## Фаза 1: Базовая структура проекта ✅ ВЫПОЛНЕНО

### 1.1 Инициализация проекта
- [x] Создать `go.mod` с зависимостями:
  - `github.com/mark3labs/mcp-go`
  - `github.com/hightemp/robotgo`
- [x] Создать базовую структуру `main.go`:
  - Парсинг аргументов командной строки (-t, -h, -p)
  - Инициализация MCP сервера
  - Запуск SSE или Stdio транспорта
- [x] Создать `Makefile` для сборки (build, build-linux, build-windows, build-darwin)
- [x] Создать `README.md` с документацией
- [x] Создать `.gitignore`
- [x] Протестировать сборку проекта

---

## Фаза 2: Mouse Control Tools (Управление мышью) ✅ ВЫПОЛНЕНО

### 2.1 Базовые операции с мышью
- [x] `mouse_move` - Перемещение курсора
  - Параметры: `x` (int, required), `y` (int, required), `display_id` (int, optional)

- [x] `mouse_move_smooth` - Плавное перемещение курсора
  - Параметры: `x` (int, required), `y` (int, required), `low` (float, optional), `high` (float, optional)

- [x] `mouse_move_relative` - Относительное перемещение
  - Параметры: `x` (int, required), `y` (int, required)

- [x] `mouse_get_position` - Получить текущую позицию курсора
  - Параметры: нет
  - Возвращает: `{x, y}`

### 2.2 Клики мыши
- [x] `mouse_click` - Клик мышью
  - Параметры: `button` (string: "left"/"right"/"center", default: "left"), `double` (bool, optional)

- [x] `mouse_click_at` - Переместить и кликнуть
  - Параметры: `x` (int, required), `y` (int, required), `button` (string, optional), `double` (bool, optional)

- [x] `mouse_toggle` - Нажать/отпустить кнопку мыши
  - Параметры: `button` (string, optional), `down` (bool: true=нажать, false=отпустить)

### 2.3 Перетаскивание
- [x] `mouse_drag` - Перетаскивание
  - Параметры: `x` (int, required), `y` (int, required), `button` (string, optional)

- [x] `mouse_drag_smooth` - Плавное перетаскивание
  - Параметры: `x` (int, required), `y` (int, required), `low` (float, optional), `high` (float, optional), `button` (string, optional)

### 2.4 Прокрутка
- [x] `mouse_scroll` - Прокрутка
  - Параметры: `x` (int, required), `y` (int, required), `display_id` (int, optional)

- [x] `mouse_scroll_direction` - Прокрутка в направлении
  - Параметры: `amount` (int, required), `direction` (string: "up"/"down"/"left"/"right", required)

- [x] `mouse_scroll_smooth` - Плавная прокрутка
  - Параметры: `to` (int, required), `num` (int, optional), `delay` (int, optional), `direction` (string, optional)

---

## Фаза 3: Keyboard Tools (Управление клавиатурой) ✅ ВЫПОЛНЕНО

### 3.1 Нажатие клавиш
- [x] `key_tap` - Нажатие клавиши
  - Параметры: `key` (string, required), `modifiers` (array of strings: "alt"/"ctrl"/"shift"/"cmd", optional)

- [x] `key_toggle` - Нажать/отпустить клавишу
  - Параметры: `key` (string, required), `down` (bool: true=нажать, false=отпустить)

### 3.2 Ввод текста
- [x] `type_text` - Ввод текста (поддержка UTF-8)
  - Параметры: `text` (string, required), `delay` (int, optional, задержка между символами в мс)

- [x] `type_text_delayed` - Ввод текста с задержкой
  - Параметры: `text` (string, required), `delay` (int, required)

### 3.3 Буфер обмена
- [x] `clipboard_read` - Прочитать из буфера обмена
  - Параметры: нет
  - Возвращает: `{text}`

- [x] `clipboard_write` - Записать в буфер обмена
  - Параметры: `text` (string, required)

- [x] `clipboard_paste` - Вставить текст через буфер обмена
  - Параметры: `text` (string, required)

---

## Фаза 4: Screen Tools (Работа с экраном) ✅ ВЫПОЛНЕНО

### 4.1 Информация об экране
- [x] `screen_get_size` - Получить размер экрана
  - Параметры: `display_id` (int, optional)
  - Возвращает: `{width, height}`

- [x] `screen_get_displays_num` - Получить количество мониторов
  - Параметры: нет
  - Возвращает: `{count}`

- [x] `screen_get_display_bounds` - Получить границы монитора
  - Параметры: `display_id` (int, required)
  - Возвращает: `{x, y, width, height}`

### 4.2 Захват экрана
- [x] `screen_capture` - Захват экрана
  - Параметры: `x` (int, optional), `y` (int, optional), `width` (int, optional), `height` (int, optional), `display_id` (int, optional)
  - Возвращает: base64 encoded PNG image

- [x] `screen_capture_save` - Захват и сохранение в файл
  - Параметры: `path` (string, required), `x` (int, optional), `y` (int, optional), `width` (int, optional), `height` (int, optional)

### 4.3 Цвет пикселя
- [x] `screen_get_pixel_color` - Получить цвет пикселя
  - Параметры: `x` (int, required), `y` (int, required), `display_id` (int, optional)
  - Возвращает: `{color}` (hex string)

- [x] `screen_get_mouse_color` - Получить цвет под курсором
  - Параметры: `display_id` (int, optional)
  - Возвращает: `{color}` (hex string)

---

## Фаза 5: Window Management Tools (Управление окнами) ✅ ВЫПОЛНЕНО

### 5.1 Информация об окнах
- [x] `window_get_active` - Получить активное окно
  - Параметры: нет
  - Возвращает: `{handle, title, pid}`

- [x] `window_get_title` - Получить заголовок окна
  - Параметры: `pid` (int, optional)
  - Возвращает: `{title}`

- [x] `window_get_bounds` - Получить границы окна
  - Параметры: `pid` (int, required)
  - Возвращает: `{x, y, width, height}`

### 5.2 Манипуляции с окнами
- [x] `window_set_active` - Активировать окно
  - Параметры: `pid` (int, required)

- [x] `window_move` - Переместить окно
  - Параметры: `pid` (int, required), `x` (int, required), `y` (int, required)

- [x] `window_resize` - Изменить размер окна
  - Параметры: `pid` (int, required), `width` (int, required), `height` (int, required)

- [x] `window_minimize` - Свернуть окно
  - Параметры: `pid` (int, required)

- [x] `window_maximize` - Развернуть окно
  - Параметры: `pid` (int, required)

- [x] `window_close` - Закрыть окно
  - Параметры: `pid` (int, optional)

---

## Фаза 6: Process Tools (Управление процессами) ✅ ВЫПОЛНЕНО

### 6.1 Информация о процессах
- [x] `process_list` - Список всех процессов
  - Параметры: нет
  - Возвращает: `[{pid, name}, ...]`

- [x] `process_find_by_name` - Найти процессы по имени
  - Параметры: `name` (string, required)
  - Возвращает: `[pid, ...]`

- [x] `process_get_name` - Получить имя процесса по PID
  - Параметры: `pid` (int, required)
  - Возвращает: `{name}`

- [x] `process_exists` - Проверить существование процесса
  - Параметры: `pid` (int, required)
  - Возвращает: `{exists}`

### 6.2 Управление процессами
- [x] `process_kill` - Завершить процесс
  - Параметры: `pid` (int, required)

- [x] `process_run` - Запустить команду
  - Параметры: `command` (string, required)
  - Возвращает: `{output}`

---

## Фаза 7: System/Utility Tools (Системные утилиты) ✅ ВЫПОЛНЕНО

### 7.1 Системная информация
- [x] `system_get_info` - Информация о системе
  - Параметры: нет
  - Возвращает: `{version, is_64bit, main_display_id, displays_count}`

### 7.2 Утилиты
- [x] `util_sleep` - Пауза
  - Параметры: `milliseconds` (int, required)

- [x] `alert_show` - Показать диалог
  - Параметры: `title` (string, required), `message` (string, required), `default_btn` (string, optional), `cancel_btn` (string, optional)
  - Возвращает: `{clicked_default}`

---

## Фаза 8: Тестирование и документация

### 8.1 Тестирование
- [ ] Протестировать все mouse tools
- [ ] Протестировать все keyboard tools
- [ ] Протестировать все screen tools
- [ ] Протестировать все window tools
- [ ] Протестировать все process tools
- [ ] Протестировать SSE транспорт
- [ ] Протестировать Stdio транспорт

### 8.2 Документация
- [x] Обновить README.md с полным описанием всех tools
- [x] Добавить примеры использования
- [x] Добавить инструкции по установке и настройке

---

## Сводка по Tools

| Категория | Количество tools | Статус |
|-----------|------------------|--------|
| Mouse Control | 12 | ✅ |
| Keyboard | 7 | ✅ |
| Screen | 7 | ✅ |
| Window Management | 9 | ✅ |
| Process Management | 6 | ✅ |
| System/Utility | 3 | ✅ |
| **Всего** | **44** | **✅** |

---

## Зависимости

```go
require (
    github.com/hightemp/robotgo v0.0.0
    github.com/mark3labs/mcp-go v0.31.0
)

replace github.com/hightemp/robotgo => ./tmp/robotgo
```

## Команды сборки

```bash
make build        # Сборка для текущей платформы
make build-linux  # Сборка для Linux
make build-windows # Сборка для Windows
make build-darwin # Сборка для macOS
make build-all    # Сборка для всех платформ
```

## Запуск

```bash
# SSE транспорт (по умолчанию)
./go_computer_use_mcp_server -t sse -h 0.0.0.0 -p 8080

# Stdio транспорт
./go_computer_use_mcp_server -t stdio
```

## Структура проекта

```
go_computer_use_mcp_server/
├── main.go                 # Основной код сервера (~900 строк)
├── go.mod                  # Go модуль
├── go.sum                  # Зависимости
├── Makefile                # Команды сборки
├── README.md               # Документация
├── TASKS.md                # План задач
├── .gitignore              # Git ignore
└── tmp/
    └── robotgo/            # Библиотека robotgo
```
