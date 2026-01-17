"""
Pytest fixtures для E2E тестирования MCP сервера.
"""

import pytest
import os
import time
import base64
from io import BytesIO
from typing import Generator, Optional
from PIL import Image

from .mcp_client import MCPClient, get_default_server_path
from .gui_helper import _GUIWindowHelper as TestWindow


# ==================== Fixtures ====================


@pytest.fixture(scope="session")
def server_path() -> str:
    """Путь к исполняемому файлу MCP сервера"""
    path = get_default_server_path()
    if not os.path.exists(path):
        pytest.skip(f"MCP server binary not found at: {path}")
    return path


@pytest.fixture(scope="session")
def mcp_client(server_path: str) -> Generator[MCPClient, None, None]:
    """
    MCP клиент для взаимодействия с сервером.
    Scope: session - один клиент на все тесты.
    """
    client = MCPClient(server_path, timeout=30.0)
    client.start()

    yield client

    client.stop()


@pytest.fixture(scope="function")
def test_window() -> Generator[TestWindow, None, None]:
    """
    Тестовое Tkinter окно.
    Scope: function - новое окно для каждого теста.
    """
    window = TestWindow()
    window.start()

    # Даём окну время появиться и стабилизироваться
    time.sleep(0.3)
    window.update()

    yield window

    window.stop()


@pytest.fixture(scope="module")
def test_window_module() -> Generator[TestWindow, None, None]:
    """
    Тестовое Tkinter окно с scope module.
    Используется для тестов, где не нужно пересоздавать окно.
    """
    window = TestWindow()
    window.start()

    time.sleep(0.3)
    window.update()

    yield window

    window.stop()


@pytest.fixture(scope="function")
def clean_test_window(test_window: TestWindow) -> TestWindow:
    """
    Тестовое окно с очищенным состоянием.
    """
    test_window.clear_state()
    test_window.clear_entry()
    test_window.update()
    return test_window


# ==================== Helper Fixtures ====================


@pytest.fixture
def temp_screenshot_path(tmp_path) -> str:
    """Временный путь для сохранения скриншотов"""
    return str(tmp_path / "screenshot.png")


@pytest.fixture
def current_pid() -> int:
    """PID текущего процесса"""
    return os.getpid()


# ==================== Helper Functions (доступны в тестах через conftest) ====================


def assert_position_near(actual: tuple, expected: tuple, tolerance: int = 5):
    """
    Проверить, что позиция близка к ожидаемой.

    Args:
        actual: Фактическая позиция (x, y)
        expected: Ожидаемая позиция (x, y)
        tolerance: Допустимое отклонение в пикселях
    """
    assert abs(actual[0] - expected[0]) <= tolerance, (
        f"X position {actual[0]} not near expected {expected[0]} (tolerance: {tolerance})"
    )
    assert abs(actual[1] - expected[1]) <= tolerance, (
        f"Y position {actual[1]} not near expected {expected[1]} (tolerance: {tolerance})"
    )


def assert_color_near(actual: str, expected: str, tolerance: int = 20):
    """
    Проверить, что цвет близок к ожидаемому.

    Args:
        actual: Фактический цвет в формате "RRGGBB" или "#RRGGBB"
        expected: Ожидаемый цвет в формате "RRGGBB" или "#RRGGBB"
        tolerance: Допустимое отклонение для каждого компонента (0-255)
    """
    # Нормализуем цвета
    actual = actual.lstrip("#").lower()
    expected = expected.lstrip("#").lower()

    # Парсим компоненты
    actual_r = int(actual[0:2], 16)
    actual_g = int(actual[2:4], 16)
    actual_b = int(actual[4:6], 16)

    expected_r = int(expected[0:2], 16)
    expected_g = int(expected[2:4], 16)
    expected_b = int(expected[4:6], 16)

    assert abs(actual_r - expected_r) <= tolerance, (
        f"Red component {actual_r} not near expected {expected_r}"
    )
    assert abs(actual_g - expected_g) <= tolerance, (
        f"Green component {actual_g} not near expected {expected_g}"
    )
    assert abs(actual_b - expected_b) <= tolerance, (
        f"Blue component {actual_b} not near expected {expected_b}"
    )


def decode_screenshot(content: dict) -> Image.Image:
    """
    Декодировать скриншот из MCP ответа.

    Args:
        content: Содержимое ответа с type="image"

    Returns:
        PIL Image объект
    """
    if isinstance(content, dict) and content.get("type") == "image":
        data = content.get("data", "")
        image_bytes = base64.b64decode(data)
        return Image.open(BytesIO(image_bytes))
    raise ValueError(f"Invalid screenshot content: {type(content)}")


def find_color_in_image(
    image: Image.Image, target_color: tuple, tolerance: int = 30
) -> bool:
    """
    Проверить, есть ли заданный цвет в изображении.

    Args:
        image: PIL Image
        target_color: RGB цвет (r, g, b)
        tolerance: Допустимое отклонение

    Returns:
        True если цвет найден
    """
    pixels = image.load()
    width, height = image.size

    for x in range(width):
        for y in range(height):
            pixel = pixels[x, y]
            # Обрабатываем RGBA и RGB
            r, g, b = pixel[0], pixel[1], pixel[2]

            if (
                abs(r - target_color[0]) <= tolerance
                and abs(g - target_color[1]) <= tolerance
                and abs(b - target_color[2]) <= tolerance
            ):
                return True

    return False


def get_color_at_region(image: Image.Image, x: int, y: int, size: int = 5) -> tuple:
    """
    Получить средний цвет в регионе изображения.

    Args:
        image: PIL Image
        x, y: Центр региона
        size: Размер региона

    Returns:
        Средний RGB цвет (r, g, b)
    """
    pixels = image.load()
    width, height = image.size

    r_sum, g_sum, b_sum = 0, 0, 0
    count = 0

    half = size // 2
    for dx in range(-half, half + 1):
        for dy in range(-half, half + 1):
            px, py = x + dx, y + dy
            if 0 <= px < width and 0 <= py < height:
                pixel = pixels[px, py]
                r_sum += pixel[0]
                g_sum += pixel[1]
                b_sum += pixel[2]
                count += 1

    if count == 0:
        return (0, 0, 0)

    return (r_sum // count, g_sum // count, b_sum // count)


def wait_for_condition(
    condition_fn, timeout: float = 5.0, interval: float = 0.1
) -> bool:
    """
    Ждать выполнения условия.

    Args:
        condition_fn: Функция, возвращающая bool
        timeout: Максимальное время ожидания
        interval: Интервал между проверками

    Returns:
        True если условие выполнилось, False по таймауту
    """
    start = time.time()
    while time.time() - start < timeout:
        if condition_fn():
            return True
        time.sleep(interval)
    return False


# Экспортируем helper функции для использования в тестах
@pytest.fixture
def helpers():
    """Набор helper функций для тестов"""

    class Helpers:
        assert_position_near = staticmethod(assert_position_near)
        assert_color_near = staticmethod(assert_color_near)
        decode_screenshot = staticmethod(decode_screenshot)
        find_color_in_image = staticmethod(find_color_in_image)
        get_color_at_region = staticmethod(get_color_at_region)
        wait_for_condition = staticmethod(wait_for_condition)

    return Helpers()


# ==================== Pytest Hooks ====================


def pytest_configure(config):
    """Конфигурация pytest"""
    # Добавляем маркеры
    config.addinivalue_line("markers", "gui: mark test as requiring GUI (X11 display)")
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_collection_modifyitems(config, items):
    """Модификация собранных тестов"""
    # Проверяем наличие DISPLAY для GUI тестов
    if not os.environ.get("DISPLAY"):
        skip_gui = pytest.mark.skip(reason="No DISPLAY environment variable")
        for item in items:
            if "gui" in item.keywords or "test_window" in item.fixturenames:
                item.add_marker(skip_gui)
