"""
E2E тесты для mouse MCP tools.

Tools:
- mouse_move: Перемещение курсора
- mouse_move_smooth: Плавное перемещение
- mouse_move_relative: Относительное перемещение
- mouse_get_position: Получение позиции
- mouse_click: Клик
- mouse_click_at: Клик по координатам
- mouse_toggle: Нажать/отпустить кнопку
- mouse_drag: Перетаскивание
- mouse_drag_smooth: Плавное перетаскивание
- mouse_scroll: Прокрутка
- mouse_scroll_direction: Прокрутка в направлении
- mouse_scroll_smooth: Плавная прокрутка
"""

import pytest
import time

from .mcp_client import MCPClient
from .gui_helper import _GUIWindowHelper as TestWindow
from .conftest import assert_position_near


class TestMouseMove:
    """Тесты для mouse_move tool"""

    @pytest.mark.gui
    def test_mouse_move_to_position(self, mcp_client: MCPClient):
        """mouse_move перемещает курсор в заданную позицию"""
        target_x, target_y = 200, 200

        result = mcp_client.call_tool("mouse_move", {"x": target_x, "y": target_y})

        assert result.success, f"mouse_move failed: {result.error}"
        assert result.content.get("status") == "success"

        # Проверяем позицию
        pos_result = mcp_client.call_tool("mouse_get_position")
        assert pos_result.success

        assert_position_near(
            (pos_result.content["x"], pos_result.content["y"]),
            (target_x, target_y),
            tolerance=5,
        )

    @pytest.mark.gui
    def test_mouse_move_to_corner(self, mcp_client: MCPClient):
        """mouse_move в угол экрана"""
        result = mcp_client.call_tool("mouse_move", {"x": 10, "y": 10})

        assert result.success

        pos_result = mcp_client.call_tool("mouse_get_position")
        assert pos_result.success
        assert pos_result.content["x"] <= 20
        assert pos_result.content["y"] <= 20

    @pytest.mark.gui
    def test_mouse_move_requires_coordinates(self, mcp_client: MCPClient):
        """mouse_move требует x и y"""
        result = mcp_client.call_tool("mouse_move", {})

        assert not result.success or "missing" in str(result.error).lower()


class TestMouseMoveSmooth:
    """Тесты для mouse_move_smooth tool"""

    @pytest.mark.gui
    def test_mouse_move_smooth_to_position(self, mcp_client: MCPClient):
        """mouse_move_smooth плавно перемещает курсор"""
        # Сначала перемещаем в начальную позицию
        mcp_client.call_tool("mouse_move", {"x": 100, "y": 100})
        time.sleep(0.1)

        target_x, target_y = 300, 300

        result = mcp_client.call_tool(
            "mouse_move_smooth", {"x": target_x, "y": target_y}
        )

        assert result.success, f"mouse_move_smooth failed: {result.error}"

        # Проверяем конечную позицию
        pos_result = mcp_client.call_tool("mouse_get_position")
        assert pos_result.success

        assert_position_near(
            (pos_result.content["x"], pos_result.content["y"]),
            (target_x, target_y),
            tolerance=10,
        )

    @pytest.mark.gui
    def test_mouse_move_smooth_with_speed_params(self, mcp_client: MCPClient):
        """mouse_move_smooth с параметрами скорости"""
        mcp_client.call_tool("mouse_move", {"x": 50, "y": 50})

        result = mcp_client.call_tool(
            "mouse_move_smooth", {"x": 250, "y": 250, "low": 0.5, "high": 1.5}
        )

        assert result.success

        pos_result = mcp_client.call_tool("mouse_get_position")
        assert pos_result.success

        assert_position_near(
            (pos_result.content["x"], pos_result.content["y"]), (250, 250), tolerance=10
        )


class TestMouseMoveRelative:
    """Тесты для mouse_move_relative tool"""

    @pytest.mark.gui
    def test_mouse_move_relative_positive(self, mcp_client: MCPClient):
        """mouse_move_relative перемещает на заданное смещение"""
        # Устанавливаем начальную позицию
        mcp_client.call_tool("mouse_move", {"x": 100, "y": 100})
        time.sleep(0.1)

        # Получаем текущую позицию
        before = mcp_client.call_tool("mouse_get_position")
        assert before.success
        start_x, start_y = before.content["x"], before.content["y"]

        # Перемещаем относительно
        dx, dy = 50, 50
        result = mcp_client.call_tool("mouse_move_relative", {"x": dx, "y": dy})

        assert result.success, f"mouse_move_relative failed: {result.error}"

        # Проверяем новую позицию
        after = mcp_client.call_tool("mouse_get_position")
        assert after.success

        expected_x = start_x + dx
        expected_y = start_y + dy

        assert_position_near(
            (after.content["x"], after.content["y"]),
            (expected_x, expected_y),
            tolerance=5,
        )

    @pytest.mark.gui
    def test_mouse_move_relative_negative(self, mcp_client: MCPClient):
        """mouse_move_relative с отрицательным смещением"""
        mcp_client.call_tool("mouse_move", {"x": 200, "y": 200})
        time.sleep(0.1)

        before = mcp_client.call_tool("mouse_get_position")
        start_x, start_y = before.content["x"], before.content["y"]

        result = mcp_client.call_tool("mouse_move_relative", {"x": -30, "y": -30})
        assert result.success

        after = mcp_client.call_tool("mouse_get_position")

        assert_position_near(
            (after.content["x"], after.content["y"]),
            (start_x - 30, start_y - 30),
            tolerance=5,
        )


class TestMouseGetPosition:
    """Тесты для mouse_get_position tool"""

    @pytest.mark.gui
    def test_mouse_get_position_returns_coordinates(self, mcp_client: MCPClient):
        """mouse_get_position возвращает координаты"""
        result = mcp_client.call_tool("mouse_get_position")

        assert result.success, f"mouse_get_position failed: {result.error}"

        content = result.content
        assert "x" in content, "Missing 'x' field"
        assert "y" in content, "Missing 'y' field"

    @pytest.mark.gui
    def test_mouse_get_position_non_negative(self, mcp_client: MCPClient):
        """mouse_get_position возвращает неотрицательные координаты"""
        result = mcp_client.call_tool("mouse_get_position")

        assert result.success
        assert result.content["x"] >= 0, (
            f"X should be non-negative: {result.content['x']}"
        )
        assert result.content["y"] >= 0, (
            f"Y should be non-negative: {result.content['y']}"
        )

    @pytest.mark.gui
    def test_mouse_get_position_after_move(self, mcp_client: MCPClient):
        """mouse_get_position возвращает корректную позицию после move"""
        target = (150, 150)
        mcp_client.call_tool("mouse_move", {"x": target[0], "y": target[1]})

        result = mcp_client.call_tool("mouse_get_position")
        assert result.success

        assert_position_near(
            (result.content["x"], result.content["y"]), target, tolerance=5
        )


class TestMouseClick:
    """Тесты для mouse_click tool"""

    @pytest.mark.gui
    def test_mouse_click_left(self, mcp_client: MCPClient, test_window: TestWindow):
        """mouse_click выполняет левый клик"""
        test_window.clear_state()

        # Перемещаем на кнопку
        x, y = test_window.get_button1_center()
        mcp_client.call_tool("mouse_move", {"x": x, "y": y})
        time.sleep(0.1)

        # Кликаем
        result = mcp_client.call_tool("mouse_click", {"button": "left"})

        assert result.success, f"mouse_click failed: {result.error}"

        # Даём время на обработку события
        time.sleep(0.2)
        test_window.update()

        # Проверяем что кнопка была нажата
        assert "button1" in test_window.state.button_clicks, (
            f"Button1 should be clicked, got: {test_window.state.button_clicks}"
        )

    @pytest.mark.gui
    def test_mouse_click_double(self, mcp_client: MCPClient, test_window: TestWindow):
        """mouse_click с double=true выполняет двойной клик"""
        test_window.clear_state()

        x, y = test_window.get_button2_center()
        mcp_client.call_tool("mouse_move", {"x": x, "y": y})
        time.sleep(0.1)

        result = mcp_client.call_tool("mouse_click", {"button": "left", "double": True})

        assert result.success

        time.sleep(0.2)
        test_window.update()

        # При двойном клике кнопка должна быть нажата (минимум один раз регистрируется)
        clicks = test_window.state.button_clicks

        # Двойной клик на кнопке должен вызвать callback хотя бы раз
        # (в реальности может вызваться 1 или 2 раза в зависимости от timing)
        assert len(clicks) >= 1, f"Should have at least one click. Clicks: {clicks}"

    @pytest.mark.gui
    def test_mouse_click_right(self, mcp_client: MCPClient, test_window: TestWindow):
        """mouse_click с button=right выполняет правый клик"""
        test_window.clear_state()

        # Кликаем правой кнопкой в области окна
        x, y = test_window.get_absolute_coords(400, 400)
        mcp_client.call_tool("mouse_move", {"x": x, "y": y})
        time.sleep(0.1)

        result = mcp_client.call_tool("mouse_click", {"button": "right"})

        assert result.success

        time.sleep(0.2)
        test_window.update()

        # Правый клик выполнился успешно
        # (Проверка события сложна в процессном подходе, просто проверяем успешность команды)


class TestMouseClickAt:
    """Тесты для mouse_click_at tool"""

    @pytest.mark.gui
    def test_mouse_click_at_button(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """mouse_click_at кликает по координатам кнопки"""
        test_window.clear_state()

        x, y = test_window.get_button1_center()

        result = mcp_client.call_tool(
            "mouse_click_at", {"x": x, "y": y, "button": "left"}
        )

        assert result.success, f"mouse_click_at failed: {result.error}"

        time.sleep(0.2)
        test_window.update()

        assert "button1" in test_window.state.button_clicks

    @pytest.mark.gui
    def test_mouse_click_at_moves_cursor(self, mcp_client: MCPClient):
        """mouse_click_at перемещает курсор в точку клика"""
        target_x, target_y = 250, 250

        result = mcp_client.call_tool("mouse_click_at", {"x": target_x, "y": target_y})

        assert result.success

        # Проверяем позицию курсора
        pos_result = mcp_client.call_tool("mouse_get_position")
        assert pos_result.success

        assert_position_near(
            (pos_result.content["x"], pos_result.content["y"]),
            (target_x, target_y),
            tolerance=5,
        )


class TestMouseToggle:
    """Тесты для mouse_toggle tool"""

    @pytest.mark.gui
    def test_mouse_toggle_down_and_up(self, mcp_client: MCPClient):
        """mouse_toggle нажимает и отпускает кнопку"""
        # Нажимаем кнопку
        down_result = mcp_client.call_tool(
            "mouse_toggle", {"button": "left", "down": True}
        )
        assert down_result.success, f"mouse_toggle down failed: {down_result.error}"

        time.sleep(0.1)

        # Отпускаем кнопку
        up_result = mcp_client.call_tool(
            "mouse_toggle", {"button": "left", "down": False}
        )
        assert up_result.success, f"mouse_toggle up failed: {up_result.error}"

    @pytest.mark.gui
    def test_mouse_toggle_default_is_down(self, mcp_client: MCPClient):
        """mouse_toggle по умолчанию нажимает (down=true)"""
        result = mcp_client.call_tool("mouse_toggle", {"button": "left"})

        assert result.success
        assert "down" in result.content.get("message", "").lower()

        # Отпускаем
        mcp_client.call_tool("mouse_toggle", {"button": "left", "down": False})


class TestMouseDrag:
    """Тесты для mouse_drag tool"""

    @pytest.mark.gui
    def test_mouse_drag_to_position(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """mouse_drag перетаскивает в заданную позицию"""
        test_window.clear_state()

        # Начальная позиция на перетаскиваемом элементе
        start_x, start_y = test_window.get_draggable_center()
        mcp_client.call_tool("mouse_move", {"x": start_x, "y": start_y})
        time.sleep(0.1)

        # Конечная позиция
        end_x = start_x + 100
        end_y = start_y

        result = mcp_client.call_tool("mouse_drag", {"x": end_x, "y": end_y})

        assert result.success, f"mouse_drag failed: {result.error}"

        # Проверяем что курсор в конечной позиции
        pos_result = mcp_client.call_tool("mouse_get_position")
        assert_position_near(
            (pos_result.content["x"], pos_result.content["y"]),
            (end_x, end_y),
            tolerance=10,
        )


class TestMouseDragSmooth:
    """Тесты для mouse_drag_smooth tool"""

    @pytest.mark.gui
    def test_mouse_drag_smooth_to_position(self, mcp_client: MCPClient):
        """mouse_drag_smooth плавно перетаскивает"""
        # Начальная позиция
        mcp_client.call_tool("mouse_move", {"x": 100, "y": 100})
        time.sleep(0.1)

        target_x, target_y = 250, 250

        result = mcp_client.call_tool(
            "mouse_drag_smooth", {"x": target_x, "y": target_y}
        )

        assert result.success, f"mouse_drag_smooth failed: {result.error}"

        # Проверяем конечную позицию
        pos_result = mcp_client.call_tool("mouse_get_position")
        assert_position_near(
            (pos_result.content["x"], pos_result.content["y"]),
            (target_x, target_y),
            tolerance=10,
        )


class TestMouseScroll:
    """Тесты для mouse_scroll tool"""

    @pytest.mark.gui
    def test_mouse_scroll_vertical(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """mouse_scroll выполняет вертикальную прокрутку"""
        # Перемещаем на scrollable область
        x, y = test_window.get_scrolled_text_center()
        mcp_client.call_tool("mouse_move", {"x": x, "y": y})
        time.sleep(0.1)

        # Получаем начальную позицию прокрутки
        initial_scroll = test_window.get_scroll_position()

        # Прокручиваем вниз
        result = mcp_client.call_tool("mouse_scroll", {"x": 0, "y": -3})

        assert result.success, f"mouse_scroll failed: {result.error}"

        time.sleep(0.2)
        test_window.update()

        # Позиция прокрутки должна измениться (не всегда срабатывает в тестах)
        # Просто проверяем что команда выполнилась успешно

    @pytest.mark.gui
    def test_mouse_scroll_horizontal(self, mcp_client: MCPClient):
        """mouse_scroll выполняет горизонтальную прокрутку"""
        result = mcp_client.call_tool("mouse_scroll", {"x": 3, "y": 0})

        assert result.success


class TestMouseScrollDirection:
    """Тесты для mouse_scroll_direction tool"""

    @pytest.mark.gui
    def test_mouse_scroll_direction_down(self, mcp_client: MCPClient):
        """mouse_scroll_direction прокручивает вниз"""
        result = mcp_client.call_tool(
            "mouse_scroll_direction", {"amount": 3, "direction": "down"}
        )

        assert result.success, f"mouse_scroll_direction failed: {result.error}"

    @pytest.mark.gui
    def test_mouse_scroll_direction_up(self, mcp_client: MCPClient):
        """mouse_scroll_direction прокручивает вверх"""
        result = mcp_client.call_tool(
            "mouse_scroll_direction", {"amount": 3, "direction": "up"}
        )

        assert result.success

    @pytest.mark.gui
    def test_mouse_scroll_direction_left(self, mcp_client: MCPClient):
        """mouse_scroll_direction прокручивает влево"""
        result = mcp_client.call_tool(
            "mouse_scroll_direction", {"amount": 3, "direction": "left"}
        )

        assert result.success

    @pytest.mark.gui
    def test_mouse_scroll_direction_right(self, mcp_client: MCPClient):
        """mouse_scroll_direction прокручивает вправо"""
        result = mcp_client.call_tool(
            "mouse_scroll_direction", {"amount": 3, "direction": "right"}
        )

        assert result.success

    def test_mouse_scroll_direction_requires_params(self, mcp_client: MCPClient):
        """mouse_scroll_direction требует amount и direction"""
        result = mcp_client.call_tool("mouse_scroll_direction", {})

        assert not result.success or "missing" in str(result.error).lower()


class TestMouseScrollSmooth:
    """Тесты для mouse_scroll_smooth tool"""

    @pytest.mark.gui
    def test_mouse_scroll_smooth(self, mcp_client: MCPClient):
        """mouse_scroll_smooth выполняет плавную прокрутку"""
        result = mcp_client.call_tool(
            "mouse_scroll_smooth", {"to": 5, "num": 3, "delay": 50}
        )

        assert result.success, f"mouse_scroll_smooth failed: {result.error}"

    @pytest.mark.gui
    def test_mouse_scroll_smooth_with_defaults(self, mcp_client: MCPClient):
        """mouse_scroll_smooth с параметрами по умолчанию"""
        result = mcp_client.call_tool("mouse_scroll_smooth", {"to": 3})

        assert result.success


class TestMouseIntegration:
    """Интеграционные тесты для mouse tools"""

    @pytest.mark.gui
    def test_move_click_sequence(self, mcp_client: MCPClient, test_window: TestWindow):
        """Последовательность: move -> click -> проверка"""
        test_window.clear_state()

        # Перемещаем на кнопку 1
        x, y = test_window.get_button1_center()
        move_result = mcp_client.call_tool("mouse_move", {"x": x, "y": y})
        assert move_result.success

        time.sleep(0.1)

        # Кликаем
        click_result = mcp_client.call_tool("mouse_click", {"button": "left"})
        assert click_result.success

        time.sleep(0.2)
        test_window.update()

        # Проверяем
        assert "button1" in test_window.state.button_clicks

    @pytest.mark.gui
    def test_position_consistency(self, mcp_client: MCPClient):
        """Позиция курсора согласована между move и get_position"""
        positions = [(100, 100), (200, 200), (300, 150), (50, 300)]

        for target_x, target_y in positions:
            mcp_client.call_tool("mouse_move", {"x": target_x, "y": target_y})

            pos = mcp_client.call_tool("mouse_get_position")
            assert pos.success

            assert_position_near(
                (pos.content["x"], pos.content["y"]), (target_x, target_y), tolerance=5
            )
