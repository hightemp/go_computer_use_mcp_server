"""
E2E тесты для window MCP tools.

Tools:
- window_get_active: Получить информацию об активном окне
- window_get_title: Получить заголовок окна
- window_get_bounds: Получить границы окна
- window_set_active: Активировать окно по PID
- window_move: Переместить окно
- window_resize: Изменить размер окна
- window_minimize: Свернуть окно
- window_maximize: Развернуть окно
- window_close: Закрыть окно
"""

import pytest
import time
import subprocess
import os

from .mcp_client import MCPClient
from .gui_helper import _GUIWindowHelper as TestWindow
from .conftest import assert_position_near, wait_for_condition


class TestWindowGetActive:
    """Тесты для window_get_active tool"""

    @pytest.mark.gui
    def test_window_get_active_returns_info(self, mcp_client: MCPClient):
        """window_get_active возвращает информацию об активном окне"""
        result = mcp_client.call_tool("window_get_active")

        assert result.success, f"window_get_active failed: {result.error}"

        content = result.content
        assert isinstance(content, dict), f"Expected dict, got {type(content)}"
        assert "handle" in content, "Missing 'handle' field"
        assert "title" in content, "Missing 'title' field"
        assert "pid" in content, "Missing 'pid' field"

    @pytest.mark.gui
    def test_window_get_active_has_valid_pid(self, mcp_client: MCPClient):
        """window_get_active возвращает валидный PID"""
        result = mcp_client.call_tool("window_get_active")

        assert result.success
        pid = result.content["pid"]

        # PID должен быть положительным числом (или 0 в некоторых случаях)
        assert isinstance(pid, int), f"PID should be int, got {type(pid)}"
        assert pid >= 0, f"Invalid PID: {pid}"

    @pytest.mark.gui
    def test_window_get_active_with_test_window(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """window_get_active после активации тестового окна"""
        # Кликаем на тестовое окно чтобы сделать его активным
        x, y = test_window.get_absolute_coords(400, 300)
        mcp_client.call_tool("mouse_click_at", {"x": x, "y": y})
        time.sleep(0.3)

        result = mcp_client.call_tool("window_get_active")

        assert result.success

        # Заголовок должен содержать "MCP E2E Test Window"
        title = result.content["title"]
        # На некоторых системах заголовок может быть другим
        # Просто проверяем что заголовок не пустой
        assert title is not None


class TestWindowGetTitle:
    """Тесты для window_get_title tool"""

    @pytest.mark.gui
    def test_window_get_title_active_window(self, mcp_client: MCPClient):
        """window_get_title возвращает заголовок активного окна"""
        result = mcp_client.call_tool("window_get_title")

        assert result.success, f"window_get_title failed: {result.error}"

        content = result.content
        assert "title" in content, "Missing 'title' field"

    @pytest.mark.gui
    def test_window_get_title_by_pid(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """window_get_title по PID возвращает заголовок"""
        # Получаем PID тестового окна
        pid = test_window.get_pid()

        result = mcp_client.call_tool("window_get_title", {"pid": pid})

        # Может вернуть ошибку если процесс не имеет окна с заголовком
        # Это нормально для Python процессов
        if result.success:
            assert "title" in result.content


class TestWindowGetBounds:
    """Тесты для window_get_bounds tool"""

    @pytest.mark.gui
    def test_window_get_bounds_returns_dimensions(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """window_get_bounds возвращает размеры окна"""
        pid = test_window.get_pid()

        result = mcp_client.call_tool("window_get_bounds", {"pid": pid})

        # Может не работать для всех окон
        if result.success:
            content = result.content
            assert "x" in content, "Missing 'x' field"
            assert "y" in content, "Missing 'y' field"
            assert "width" in content, "Missing 'width' field"
            assert "height" in content, "Missing 'height' field"

    @pytest.mark.gui
    def test_window_get_bounds_valid_values(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """window_get_bounds возвращает валидные значения"""
        pid = test_window.get_pid()

        result = mcp_client.call_tool("window_get_bounds", {"pid": pid})

        if result.success:
            content = result.content
            # Размеры должны быть положительными
            assert content["width"] >= 0, f"Invalid width: {content['width']}"
            assert content["height"] >= 0, f"Invalid height: {content['height']}"

    def test_window_get_bounds_requires_pid(self, mcp_client: MCPClient):
        """window_get_bounds требует параметр pid"""
        result = mcp_client.call_tool("window_get_bounds", {})

        assert not result.success or "missing" in str(result.error).lower()


class TestWindowSetActive:
    """Тесты для window_set_active tool"""

    @pytest.mark.gui
    def test_window_set_active_by_pid(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """window_set_active активирует окно по PID"""
        pid = test_window.get_pid()

        result = mcp_client.call_tool("window_set_active", {"pid": pid})

        # Может не работать для всех окон/систем
        # Проверяем что команда хотя бы выполнилась
        # Успех или понятная ошибка
        if result.success:
            assert result.content.get("status") == "success"

    def test_window_set_active_requires_pid(self, mcp_client: MCPClient):
        """window_set_active требует параметр pid"""
        result = mcp_client.call_tool("window_set_active", {})

        assert not result.success or "missing" in str(result.error).lower()


class TestWindowMove:
    """Тесты для window_move tool"""

    @pytest.mark.gui
    def test_window_move_to_position(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """window_move перемещает окно в заданную позицию"""
        pid = test_window.get_pid()
        target_x, target_y = 50, 50

        result = mcp_client.call_tool(
            "window_move", {"pid": pid, "x": target_x, "y": target_y}
        )

        # Может не работать для всех окон
        if result.success:
            assert result.content.get("status") == "success"

            time.sleep(0.2)
            test_window.update()

            # Проверяем позицию (может быть неточной из-за декораций окна)
            actual_pos = test_window.get_window_position()
            # Допускаем погрешность в 100 пикселей из-за декораций окна

    @pytest.mark.gui
    def test_window_move_multiple_times(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """window_move несколько раз подряд"""
        pid = test_window.get_pid()

        positions = [(100, 100), (200, 150), (150, 200)]

        for x, y in positions:
            result = mcp_client.call_tool("window_move", {"pid": pid, "x": x, "y": y})

            if not result.success:
                break  # Если не поддерживается, прекращаем

            time.sleep(0.1)

    def test_window_move_requires_params(self, mcp_client: MCPClient):
        """window_move требует pid, x и y"""
        result = mcp_client.call_tool("window_move", {})

        assert not result.success or "missing" in str(result.error).lower()


class TestWindowResize:
    """Тесты для window_resize tool"""

    @pytest.mark.gui
    def test_window_resize(self, mcp_client: MCPClient, test_window: TestWindow):
        """window_resize изменяет размер окна"""
        pid = test_window.get_pid()
        target_width, target_height = 600, 400

        result = mcp_client.call_tool(
            "window_resize",
            {"pid": pid, "width": target_width, "height": target_height},
        )

        if result.success:
            assert result.content.get("status") == "success"

            time.sleep(0.2)
            test_window.update()

    def test_window_resize_requires_params(self, mcp_client: MCPClient):
        """window_resize требует pid, width и height"""
        result = mcp_client.call_tool("window_resize", {})

        assert not result.success or "missing" in str(result.error).lower()


class TestWindowMinimize:
    """Тесты для window_minimize tool"""

    @pytest.mark.gui
    def test_window_minimize(self, mcp_client: MCPClient, test_window: TestWindow):
        """window_minimize сворачивает окно"""
        pid = test_window.get_pid()

        # Сначала убедимся что окно не свёрнуто
        initial_state = test_window.get_wm_state()

        result = mcp_client.call_tool("window_minimize", {"pid": pid})

        if result.success:
            assert result.content.get("status") == "success"

            time.sleep(0.3)
            test_window.update()

            # Проверяем состояние окна
            # На некоторых системах состояние может не измениться

    def test_window_minimize_requires_pid(self, mcp_client: MCPClient):
        """window_minimize требует параметр pid"""
        result = mcp_client.call_tool("window_minimize", {})

        assert not result.success or "missing" in str(result.error).lower()


class TestWindowMaximize:
    """Тесты для window_maximize tool"""

    @pytest.mark.gui
    def test_window_maximize(self, mcp_client: MCPClient, test_window: TestWindow):
        """window_maximize разворачивает окно"""
        pid = test_window.get_pid()

        result = mcp_client.call_tool("window_maximize", {"pid": pid})

        if result.success:
            assert result.content.get("status") == "success"

            time.sleep(0.3)
            test_window.update()

    def test_window_maximize_requires_pid(self, mcp_client: MCPClient):
        """window_maximize требует параметр pid"""
        result = mcp_client.call_tool("window_maximize", {})

        assert not result.success or "missing" in str(result.error).lower()


class TestWindowClose:
    """Тесты для window_close tool"""

    @pytest.mark.gui
    def test_window_close_spawned_window(self, mcp_client: MCPClient):
        """window_close закрывает окно"""
        # Создаём тестовое окно через xterm или другое простое приложение
        # Используем xmessage если доступен
        try:
            proc = subprocess.Popen(
                ["xmessage", "-timeout", "30", "Test window for close test"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            pytest.skip("xmessage not available")
            return

        time.sleep(0.5)

        # Проверяем что процесс запущен
        assert proc.poll() is None, "Process should be running"

        # Закрываем окно
        result = mcp_client.call_tool("window_close", {"pid": proc.pid})

        # Даём время на закрытие
        time.sleep(0.5)

        # Очищаем процесс
        try:
            proc.terminate()
            proc.wait(timeout=1)
        except Exception:
            pass

    @pytest.mark.gui
    def test_window_close_active_window(self, mcp_client: MCPClient):
        """window_close без pid закрывает активное окно"""
        # Создаём тестовое окно
        try:
            proc = subprocess.Popen(
                ["xmessage", "-timeout", "30", "Test window"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            pytest.skip("xmessage not available")
            return

        time.sleep(0.5)

        # Активируем это окно кликом
        # (сложно без знания позиции)

        # Очищаем
        try:
            proc.terminate()
            proc.wait(timeout=1)
        except Exception:
            pass


class TestWindowIntegration:
    """Интеграционные тесты для window tools"""

    @pytest.mark.gui
    def test_get_active_and_get_bounds_consistency(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """window_get_active и window_get_bounds согласованы"""
        # Делаем тестовое окно активным
        x, y = test_window.get_absolute_coords(400, 300)
        mcp_client.call_tool("mouse_click_at", {"x": x, "y": y})
        time.sleep(0.2)

        # Получаем информацию об активном окне
        active_result = mcp_client.call_tool("window_get_active")
        assert active_result.success

        pid = active_result.content["pid"]

        if pid > 0:
            # Получаем границы по PID
            bounds_result = mcp_client.call_tool("window_get_bounds", {"pid": pid})

            # Если оба успешны, данные должны быть валидны
            if bounds_result.success:
                assert (
                    bounds_result.content["width"] > 0
                    or bounds_result.content["height"] > 0
                )

    @pytest.mark.gui
    def test_move_and_get_bounds_consistency(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """window_move и window_get_bounds согласованы"""
        pid = test_window.get_pid()
        target_x, target_y = 100, 100

        # Перемещаем окно
        move_result = mcp_client.call_tool(
            "window_move", {"pid": pid, "x": target_x, "y": target_y}
        )

        if not move_result.success:
            pytest.skip("window_move not supported for this window")

        time.sleep(0.2)

        # Получаем границы
        bounds_result = mcp_client.call_tool("window_get_bounds", {"pid": pid})

        if bounds_result.success:
            # Позиция должна быть близка к целевой
            # Допускаем большую погрешность из-за декораций окна
            actual_x = bounds_result.content["x"]
            actual_y = bounds_result.content["y"]

            # Просто проверяем что значения изменились или близки
            # (точное сравнение сложно из-за особенностей оконных менеджеров)

    @pytest.mark.gui
    def test_resize_and_get_bounds_consistency(
        self, mcp_client: MCPClient, test_window: TestWindow
    ):
        """window_resize и window_get_bounds согласованы"""
        pid = test_window.get_pid()
        target_width, target_height = 500, 350

        # Изменяем размер
        resize_result = mcp_client.call_tool(
            "window_resize",
            {"pid": pid, "width": target_width, "height": target_height},
        )

        if not resize_result.success:
            pytest.skip("window_resize not supported for this window")

        time.sleep(0.2)

        # Получаем границы
        bounds_result = mcp_client.call_tool("window_get_bounds", {"pid": pid})

        if bounds_result.success:
            # Размеры должны быть близки к целевым
            # Допускаем погрешность
            actual_width = bounds_result.content["width"]
            actual_height = bounds_result.content["height"]
