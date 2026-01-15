# go_computer_use_mcp_server

MCP (Model Context Protocol) сервер на Go для управления компьютером. Использует библиотеку [robotgo](https://github.com/hightemp/robotgo) для автоматизации.

## Возможности

- **Управление мышью**: перемещение, клики, перетаскивание, прокрутка
- **Управление клавиатурой**: нажатие клавиш, ввод текста, горячие клавиши
- **Работа с экраном**: захват скриншотов, получение цвета пикселя, информация о дисплеях
- **Управление окнами**: перемещение, изменение размера, сворачивание/разворачивание
- **Управление процессами**: список процессов, поиск, завершение
- **Системные утилиты**: информация о системе, диалоги, паузы

## Установка

### Требования

- Go 1.21+
- Для Linux: `libx11-dev`, `libxtst-dev`, `libxinerama-dev`, `libxcursor-dev`, `libxkbcommon-dev`

```bash
# Ubuntu/Debian
sudo apt-get install libx11-dev libxtst-dev libxinerama-dev libxcursor-dev libxkbcommon-dev

# Fedora
sudo dnf install libX11-devel libXtst-devel libXinerama-devel libXcursor-devel libxkbcommon-devel
```

### Сборка

```bash
# Скачать зависимости
make deps

# Собрать для текущей платформы
make build

# Собрать для всех платформ
make build-all
```

## Запуск

### SSE транспорт (по умолчанию)

```bash
./go_computer_use_mcp_server -t sse -h 0.0.0.0 -p 8080
```

### Stdio транспорт

```bash
./go_computer_use_mcp_server -t stdio
```

### Параметры командной строки

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `-t` | Транспорт: `sse` или `stdio` | `sse` |
| `-h` | Хост для SSE сервера | `0.0.0.0` |
| `-p` | Порт для SSE сервера | `8080` |

## Доступные инструменты (Tools)

### Управление мышью (12 tools)

| Tool | Описание |
|------|----------|
| `mouse_move` | Перемещение курсора в абсолютные координаты |
| `mouse_move_smooth` | Плавное перемещение курсора |
| `mouse_move_relative` | Относительное перемещение курсора |
| `mouse_get_position` | Получить текущую позицию курсора |
| `mouse_click` | Клик мышью |
| `mouse_click_at` | Переместить и кликнуть |
| `mouse_toggle` | Нажать/отпустить кнопку мыши |
| `mouse_drag` | Перетаскивание |
| `mouse_drag_smooth` | Плавное перетаскивание |
| `mouse_scroll` | Прокрутка |
| `mouse_scroll_direction` | Прокрутка в направлении |
| `mouse_scroll_smooth` | Плавная прокрутка |

### Управление клавиатурой (7 tools)

| Tool | Описание |
|------|----------|
| `key_tap` | Нажатие клавиши (с модификаторами) |
| `key_toggle` | Нажать/отпустить клавишу |
| `type_text` | Ввод текста (UTF-8) |
| `type_text_delayed` | Ввод текста с задержкой |
| `clipboard_read` | Прочитать буфер обмена |
| `clipboard_write` | Записать в буфер обмена |
| `clipboard_paste` | Вставить через буфер обмена |

### Работа с экраном (7 tools)

| Tool | Описание |
|------|----------|
| `screen_get_size` | Получить размер экрана |
| `screen_get_displays_num` | Количество мониторов |
| `screen_get_display_bounds` | Границы монитора |
| `screen_capture` | Захват экрана (base64 PNG) |
| `screen_capture_save` | Захват и сохранение в файл |
| `screen_get_pixel_color` | Цвет пикселя по координатам |
| `screen_get_mouse_color` | Цвет под курсором |

### Управление окнами (9 tools)

| Tool | Описание |
|------|----------|
| `window_get_active` | Информация об активном окне |
| `window_get_title` | Заголовок окна |
| `window_get_bounds` | Границы окна |
| `window_set_active` | Активировать окно |
| `window_move` | Переместить окно |
| `window_resize` | Изменить размер окна |
| `window_minimize` | Свернуть окно |
| `window_maximize` | Развернуть окно |
| `window_close` | Закрыть окно |

### Управление процессами (6 tools)

| Tool | Описание |
|------|----------|
| `process_list` | Список всех процессов |
| `process_find_by_name` | Найти процессы по имени |
| `process_get_name` | Имя процесса по PID |
| `process_exists` | Проверить существование процесса |
| `process_kill` | Завершить процесс |
| `process_run` | Запустить команду |

### Системные утилиты (3 tools)

| Tool | Описание |
|------|----------|
| `system_get_info` | Информация о системе |
| `util_sleep` | Пауза |
| `alert_show` | Показать диалог |

## Примеры использования

### Перемещение мыши и клик

```json
{
  "tool": "mouse_click_at",
  "arguments": {
    "x": 100,
    "y": 200,
    "button": "left",
    "double": false
  }
}
```

### Ввод текста

```json
{
  "tool": "type_text",
  "arguments": {
    "text": "Hello, World!",
    "delay": 50
  }
}
```

### Горячие клавиши

```json
{
  "tool": "key_tap",
  "arguments": {
    "key": "c",
    "modifiers": ["ctrl"]
  }
}
```

### Захват экрана

```json
{
  "tool": "screen_capture",
  "arguments": {
    "x": 0,
    "y": 0,
    "width": 800,
    "height": 600
  }
}
```

## Поддерживаемые клавиши

### Буквы и цифры
`a-z`, `A-Z`, `0-9`

### Функциональные клавиши
`f1`-`f24`

### Навигация
`up`, `down`, `left`, `right`, `home`, `end`, `pageup`, `pagedown`

### Специальные
`backspace`, `delete`, `enter`, `tab`, `escape`, `space`, `insert`, `capslock`

### Модификаторы
`alt`, `ctrl`, `shift`, `cmd` (или `command`)

### Мультимедиа
`audio_mute`, `audio_vol_down`, `audio_vol_up`, `audio_play`, `audio_stop`, `audio_pause`

## Лицензия

MIT
