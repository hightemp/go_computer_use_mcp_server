"""
E2E тесты для MCP сервера go_computer_use_mcp_server.

Структура тестов:
- test_system.py - системные tools (system_get_info, util_sleep)
- test_process.py - процессы (process_list, process_run, и т.д.)
- test_screen.py - экран (screen_capture, screen_get_size, и т.д.)
- test_mouse.py - мышь (mouse_move, mouse_click, и т.д.)
- test_keyboard.py - клавиатура (key_tap, type_text, и т.д.)
- test_window_tools.py - окна (window_get_active, window_move, и т.д.)

Запуск тестов:
    pytest tests/ -v

Запуск конкретной категории:
    pytest tests/test_mouse.py -v

Запуск с пропуском GUI тестов (без DISPLAY):
    pytest tests/ -v -m "not gui"
"""
