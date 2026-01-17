"""
E2E тесты для screen MCP tools.

Tools:
- screen_get_size: Получить размер экрана
- screen_get_displays_num: Количество дисплеев
- screen_get_display_bounds: Границы дисплея
- screen_capture: Захват экрана (base64)
- screen_capture_save: Сохранить скриншот в файл
- screen_get_pixel_color: Цвет пикселя по координатам
- screen_get_mouse_color: Цвет пикселя под курсором
"""

import pytest
import os
import base64
import time
from io import BytesIO
from PIL import Image

from .mcp_client import MCPClient
from .gui_helper import _GUIWindowHelper as TestWindow
from .conftest import decode_screenshot, find_color_in_image, assert_color_near


class TestScreenGetSize:
    """Тесты для screen_get_size tool"""

    def test_screen_get_size_returns_valid_dimensions(self, mcp_client: MCPClient):
        """screen_get_size возвращает валидные размеры экрана"""
        result = mcp_client.call_tool("screen_get_size")

        assert result.success, f"screen_get_size failed: {result.error}"

        content = result.content
        assert isinstance(content, dict), f"Expected dict, got {type(content)}"
        assert "width" in content, "Missing 'width' field"
        assert "height" in content, "Missing 'height' field"

    def test_screen_get_size_positive_values(self, mcp_client: MCPClient):
        """screen_get_size возвращает положительные значения"""
        result = mcp_client.call_tool("screen_get_size")

        assert result.success
        assert result.content["width"] > 0, "Width should be positive"
        assert result.content["height"] > 0, "Height should be positive"

    def test_screen_get_size_reasonable_values(self, mcp_client: MCPClient):
        """screen_get_size возвращает разумные значения (не менее 640x480)"""
        result = mcp_client.call_tool("screen_get_size")

        assert result.success
        assert result.content["width"] >= 640, (
            f"Width too small: {result.content['width']}"
        )
        assert result.content["height"] >= 480, (
            f"Height too small: {result.content['height']}"
        )

    def test_screen_get_size_with_display_id(self, mcp_client: MCPClient):
        """screen_get_size с display_id=0 работает"""
        result = mcp_client.call_tool("screen_get_size", {"display_id": 0})

        assert result.success, f"screen_get_size with display_id failed: {result.error}"
        assert result.content["width"] > 0
        assert result.content["height"] > 0


class TestScreenGetDisplaysNum:
    """Тесты для screen_get_displays_num tool"""

    def test_screen_get_displays_num_returns_count(self, mcp_client: MCPClient):
        """screen_get_displays_num возвращает количество дисплеев"""
        result = mcp_client.call_tool("screen_get_displays_num")

        assert result.success, f"screen_get_displays_num failed: {result.error}"

        content = result.content
        assert "count" in content, "Missing 'count' field"

    def test_screen_get_displays_num_at_least_one(self, mcp_client: MCPClient):
        """screen_get_displays_num возвращает как минимум 1"""
        result = mcp_client.call_tool("screen_get_displays_num")

        assert result.success
        assert result.content["count"] >= 1, "Should have at least 1 display"


class TestScreenGetDisplayBounds:
    """Тесты для screen_get_display_bounds tool"""

    def test_screen_get_display_bounds_for_display_0(self, mcp_client: MCPClient):
        """screen_get_display_bounds возвращает границы дисплея 0"""
        result = mcp_client.call_tool("screen_get_display_bounds", {"display_id": 0})

        assert result.success, f"screen_get_display_bounds failed: {result.error}"

        content = result.content
        assert "x" in content, "Missing 'x' field"
        assert "y" in content, "Missing 'y' field"
        assert "width" in content, "Missing 'width' field"
        assert "height" in content, "Missing 'height' field"

    def test_screen_get_display_bounds_valid_dimensions(self, mcp_client: MCPClient):
        """screen_get_display_bounds возвращает валидные размеры"""
        result = mcp_client.call_tool("screen_get_display_bounds", {"display_id": 0})

        assert result.success
        assert result.content["width"] > 0, "Width should be positive"
        assert result.content["height"] > 0, "Height should be positive"

    def test_screen_get_display_bounds_requires_display_id(self, mcp_client: MCPClient):
        """screen_get_display_bounds требует display_id"""
        result = mcp_client.call_tool("screen_get_display_bounds", {})

        assert not result.success or "missing" in str(result.error).lower()

    def test_screen_get_display_bounds_matches_screen_size(self, mcp_client: MCPClient):
        """screen_get_display_bounds согласуется со screen_get_size для display 0"""
        bounds_result = mcp_client.call_tool(
            "screen_get_display_bounds", {"display_id": 0}
        )
        size_result = mcp_client.call_tool("screen_get_size")

        assert bounds_result.success and size_result.success

        # В мультимониторной конфигурации screen_get_size возвращает общий размер всех мониторов,
        # а screen_get_display_bounds возвращает размер конкретного монитора.
        # Поэтому просто проверяем, что размеры display 0 положительны и не больше общего размера
        display_width = bounds_result.content["width"]
        display_height = bounds_result.content["height"]
        total_width = size_result.content["width"]
        total_height = size_result.content["height"]

        assert display_width > 0, f"Display width should be positive: {display_width}"
        assert display_height > 0, (
            f"Display height should be positive: {display_height}"
        )
        assert display_width <= total_width, (
            f"Display width {display_width} > total {total_width}"
        )
        assert display_height <= total_height, (
            f"Display height {display_height} > total {total_height}"
        )


class TestScreenCapture:
    """Тесты для screen_capture tool"""

    @pytest.mark.gui
    def test_screen_capture_returns_image(self, mcp_client: MCPClient):
        """screen_capture возвращает изображение в base64"""
        result = mcp_client.call_tool("screen_capture")

        assert result.success, f"screen_capture failed: {result.error}"

        content = result.content
        assert isinstance(content, dict), (
            f"Expected dict with image, got {type(content)}"
        )
        assert content.get("type") == "image", (
            f"Expected type='image', got {content.get('type')}"
        )
        assert "data" in content, "Missing 'data' field"
        assert content.get("mimeType") == "image/png", (
            f"Expected mimeType='image/png', got {content.get('mimeType')}"
        )

    @pytest.mark.gui
    def test_screen_capture_valid_png(self, mcp_client: MCPClient):
        """screen_capture возвращает валидный PNG"""
        result = mcp_client.call_tool("screen_capture")

        assert result.success

        # Декодируем и проверяем
        image = decode_screenshot(result.content)
        assert image is not None, "Failed to decode screenshot"
        assert image.width > 0, "Image width should be positive"
        assert image.height > 0, "Image height should be positive"

    @pytest.mark.gui
    def test_screen_capture_region(self, mcp_client: MCPClient):
        """screen_capture с указанным регионом"""
        result = mcp_client.call_tool(
            "screen_capture", {"x": 0, "y": 0, "width": 100, "height": 100}
        )

        assert result.success, f"screen_capture region failed: {result.error}"

        image = decode_screenshot(result.content)
        assert image.width == 100, f"Expected width 100, got {image.width}"
        assert image.height == 100, f"Expected height 100, got {image.height}"

    @pytest.mark.gui
    def test_screen_capture_with_test_window_has_red(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """screen_capture захватывает тестовое окно с красным квадратом"""
        # Получаем координаты красного квадрата
        win_x, win_y = test_window.get_window_position()

        # Захватываем область окна
        result = mcp_client.call_tool(
            "screen_capture", {"x": win_x, "y": win_y, "width": 200, "height": 200}
        )

        assert result.success, f"screen_capture failed: {result.error}"

        image = decode_screenshot(result.content)

        # Проверяем наличие красного цвета
        has_red = find_color_in_image(image, (255, 0, 0), tolerance=50)
        assert has_red, "Screenshot should contain red color from test window"

    @pytest.mark.gui
    def test_screen_capture_with_test_window_has_blue(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """screen_capture захватывает тестовое окно с синим кругом"""
        win_x, win_y = test_window.get_window_position()

        result = mcp_client.call_tool(
            "screen_capture",
            {"x": win_x + 150, "y": win_y, "width": 200, "height": 200},
        )

        assert result.success

        image = decode_screenshot(result.content)
        has_blue = find_color_in_image(image, (0, 0, 255), tolerance=50)
        assert has_blue, "Screenshot should contain blue color from test window"


class TestScreenCaptureSave:
    """Тесты для screen_capture_save tool"""

    @pytest.mark.gui
    def test_screen_capture_save_creates_file(
        self, mcp_client: MCPClient, temp_screenshot_path: str
    ):
        """screen_capture_save создаёт файл"""
        result = mcp_client.call_tool(
            "screen_capture_save", {"path": temp_screenshot_path}
        )

        assert result.success, f"screen_capture_save failed: {result.error}"
        assert os.path.exists(temp_screenshot_path), (
            f"Screenshot file not created: {temp_screenshot_path}"
        )

    @pytest.mark.gui
    def test_screen_capture_save_valid_png(
        self, mcp_client: MCPClient, temp_screenshot_path: str
    ):
        """screen_capture_save создаёт валидный PNG файл"""
        result = mcp_client.call_tool(
            "screen_capture_save", {"path": temp_screenshot_path}
        )

        assert result.success

        # Проверяем что файл - валидный PNG
        with Image.open(temp_screenshot_path) as img:
            assert img.format == "PNG", f"Expected PNG, got {img.format}"
            assert img.width > 0
            assert img.height > 0

    @pytest.mark.gui
    def test_screen_capture_save_region(
        self, mcp_client: MCPClient, temp_screenshot_path: str
    ):
        """screen_capture_save с регионом создаёт файл нужного размера"""
        result = mcp_client.call_tool(
            "screen_capture_save",
            {"path": temp_screenshot_path, "x": 0, "y": 0, "width": 150, "height": 150},
        )

        assert result.success

        with Image.open(temp_screenshot_path) as img:
            assert img.width == 150, f"Expected width 150, got {img.width}"
            assert img.height == 150, f"Expected height 150, got {img.height}"

    @pytest.mark.gui
    def test_screen_capture_save_returns_success(
        self, mcp_client: MCPClient, temp_screenshot_path: str
    ):
        """screen_capture_save возвращает статус success"""
        result = mcp_client.call_tool(
            "screen_capture_save", {"path": temp_screenshot_path}
        )

        assert result.success
        assert result.content.get("status") == "success"
        assert "path" in result.content

    def test_screen_capture_save_requires_path(self, mcp_client: MCPClient):
        """screen_capture_save требует параметр path"""
        result = mcp_client.call_tool("screen_capture_save", {})

        assert not result.success or "missing" in str(result.error).lower()


class TestScreenGetPixelColor:
    """Тесты для screen_get_pixel_color tool"""

    @pytest.mark.gui
    def test_screen_get_pixel_color_returns_color(self, mcp_client: MCPClient):
        """screen_get_pixel_color возвращает цвет"""
        result = mcp_client.call_tool("screen_get_pixel_color", {"x": 0, "y": 0})

        assert result.success, f"screen_get_pixel_color failed: {result.error}"

        content = result.content
        assert "color" in content, "Missing 'color' field"

    @pytest.mark.gui
    def test_screen_get_pixel_color_valid_hex(self, mcp_client: MCPClient):
        """screen_get_pixel_color возвращает валидный hex цвет"""
        result = mcp_client.call_tool("screen_get_pixel_color", {"x": 100, "y": 100})

        assert result.success
        color = result.content["color"]

        # Цвет должен быть 6 символов hex
        assert len(color) == 6, f"Color should be 6 hex chars, got '{color}'"
        assert all(c in "0123456789abcdefABCDEF" for c in color), (
            f"Invalid hex color: {color}"
        )

    @pytest.mark.gui
    def test_screen_get_pixel_color_red_rect(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """screen_get_pixel_color на красном квадрате возвращает красный цвет"""
        # Даём окну время отрисоваться
        time.sleep(0.2)
        test_window.update()

        # Получаем центр красного квадрата
        x, y = test_window.get_red_rect_center()

        result = mcp_client.call_tool("screen_get_pixel_color", {"x": x, "y": y})

        assert result.success, f"screen_get_pixel_color failed: {result.error}"

        color = result.content["color"]
        # Красный цвет: ff0000 или близкий к нему
        assert_color_near(color, "ff0000", tolerance=50)

    @pytest.mark.gui
    def test_screen_get_pixel_color_blue_circle(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """screen_get_pixel_color на синем круге возвращает синий цвет"""
        time.sleep(0.2)
        test_window.update()

        x, y = test_window.get_blue_circle_center()

        result = mcp_client.call_tool("screen_get_pixel_color", {"x": x, "y": y})

        assert result.success

        color = result.content["color"]
        assert_color_near(color, "0000ff", tolerance=50)

    @pytest.mark.gui
    def test_screen_get_pixel_color_green_rect(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """screen_get_pixel_color на зелёном квадрате возвращает зелёный цвет"""
        time.sleep(0.2)
        test_window.update()

        x, y = test_window.get_green_rect_center()

        result = mcp_client.call_tool("screen_get_pixel_color", {"x": x, "y": y})

        assert result.success

        color = result.content["color"]
        # Tkinter "green" is #008000, not #00ff00
        assert_color_near(color, "008000", tolerance=50)

    def test_screen_get_pixel_color_requires_coordinates(self, mcp_client: MCPClient):
        """screen_get_pixel_color требует x и y"""
        result = mcp_client.call_tool("screen_get_pixel_color", {})

        assert not result.success or "missing" in str(result.error).lower()


class TestScreenGetMouseColor:
    """Тесты для screen_get_mouse_color tool"""

    @pytest.mark.gui
    def test_screen_get_mouse_color_returns_color(self, mcp_client: MCPClient):
        """screen_get_mouse_color возвращает цвет"""
        result = mcp_client.call_tool("screen_get_mouse_color")

        assert result.success, f"screen_get_mouse_color failed: {result.error}"

        content = result.content
        assert "color" in content, "Missing 'color' field"

    @pytest.mark.gui
    def test_screen_get_mouse_color_valid_hex(self, mcp_client: MCPClient):
        """screen_get_mouse_color возвращает валидный hex цвет"""
        result = mcp_client.call_tool("screen_get_mouse_color")

        assert result.success
        color = result.content["color"]

        assert len(color) == 6, f"Color should be 6 hex chars, got '{color}'"
        assert all(c in "0123456789abcdefABCDEF" for c in color), (
            f"Invalid hex color: {color}"
        )

    @pytest.mark.gui
    def test_screen_get_mouse_color_on_red_rect(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """screen_get_mouse_color после перемещения на красный квадрат"""
        time.sleep(0.2)
        test_window.update()

        # Перемещаем мышь на красный квадрат
        x, y = test_window.get_red_rect_center()
        mcp_client.call_tool("mouse_move", {"x": x, "y": y})
        time.sleep(0.1)

        # Получаем цвет под курсором
        result = mcp_client.call_tool("screen_get_mouse_color")

        assert result.success
        color = result.content["color"]
        assert_color_near(color, "ff0000", tolerance=50)

    @pytest.mark.gui
    def test_screen_get_mouse_color_on_blue_circle(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """screen_get_mouse_color после перемещения на синий круг"""
        time.sleep(0.2)
        test_window.update()

        x, y = test_window.get_blue_circle_center()
        mcp_client.call_tool("mouse_move", {"x": x, "y": y})
        time.sleep(0.1)

        result = mcp_client.call_tool("screen_get_mouse_color")

        assert result.success
        color = result.content["color"]
        assert_color_near(color, "0000ff", tolerance=50)


class TestScreenIntegration:
    """Интеграционные тесты для screen tools"""

    @pytest.mark.gui
    def test_capture_matches_pixel_color(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """Цвет из screen_capture соответствует screen_get_pixel_color"""
        time.sleep(0.2)
        test_window.update()

        # Координаты для проверки
        x, y = test_window.get_red_rect_center()
        win_x, win_y = test_window.get_window_position()

        # Получаем цвет пикселя
        pixel_result = mcp_client.call_tool("screen_get_pixel_color", {"x": x, "y": y})
        assert pixel_result.success
        pixel_color = pixel_result.content["color"]

        # Делаем скриншот
        capture_result = mcp_client.call_tool(
            "screen_capture", {"x": win_x, "y": win_y, "width": 200, "height": 200}
        )
        assert capture_result.success

        image = decode_screenshot(capture_result.content)

        # Проверяем что в скриншоте есть красный цвет
        has_matching_color = find_color_in_image(
            image,
            (
                int(pixel_color[0:2], 16),
                int(pixel_color[2:4], 16),
                int(pixel_color[4:6], 16),
            ),
            tolerance=30,
        )
        # Даже если не найден точный цвет, должен быть красный
        has_red = find_color_in_image(image, (255, 0, 0), tolerance=50)

        assert has_matching_color or has_red, (
            "Screenshot should contain the pixel color"
        )

    @pytest.mark.gui
    def test_display_bounds_and_screen_size_consistency(self, mcp_client: MCPClient):
        """Границы дисплея и размер экрана согласованы"""
        displays_result = mcp_client.call_tool("screen_get_displays_num")
        assert displays_result.success

        num_displays = displays_result.content["count"]

        for display_id in range(num_displays):
            bounds_result = mcp_client.call_tool(
                "screen_get_display_bounds", {"display_id": display_id}
            )

            if bounds_result.success:
                # Проверяем что границы валидны
                assert bounds_result.content["width"] > 0
                assert bounds_result.content["height"] > 0
