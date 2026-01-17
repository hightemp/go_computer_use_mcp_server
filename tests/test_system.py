"""
E2E тесты для системных MCP tools.

Tools:
- system_get_info: Получить информацию о системе
- util_sleep: Пауза на заданное время
- alert_show: (пропускаем - требует интерактивности)
"""

import pytest
import time

from .mcp_client import MCPClient


class TestSystemGetInfo:
    """Тесты для system_get_info tool"""

    def test_system_get_info_returns_valid_data(self, mcp_client: MCPClient):
        """system_get_info возвращает корректные данные о системе"""
        result = mcp_client.call_tool("system_get_info")

        assert result.success, f"system_get_info failed: {result.error}"

        content = result.content
        assert isinstance(content, dict), f"Expected dict, got {type(content)}"

        # Проверяем наличие обязательных полей
        assert "version" in content, "Missing 'version' field"
        assert "is_64bit" in content, "Missing 'is_64bit' field"
        assert "main_display_id" in content, "Missing 'main_display_id' field"
        assert "displays_count" in content, "Missing 'displays_count' field"

    def test_system_get_info_version_not_empty(self, mcp_client: MCPClient):
        """system_get_info возвращает непустую версию"""
        result = mcp_client.call_tool("system_get_info")

        assert result.success
        assert result.content["version"], "Version should not be empty"

    def test_system_get_info_displays_count_positive(self, mcp_client: MCPClient):
        """system_get_info возвращает положительное количество дисплеев"""
        result = mcp_client.call_tool("system_get_info")

        assert result.success
        assert result.content["displays_count"] >= 1, "Should have at least 1 display"

    def test_system_get_info_is_64bit_is_boolean(self, mcp_client: MCPClient):
        """system_get_info возвращает булево значение для is_64bit"""
        result = mcp_client.call_tool("system_get_info")

        assert result.success
        assert isinstance(result.content["is_64bit"], bool), (
            "is_64bit should be boolean"
        )


class TestUtilSleep:
    """Тесты для util_sleep tool"""

    def test_util_sleep_100ms(self, mcp_client: MCPClient):
        """util_sleep с 100ms занимает примерно 100ms"""
        start = time.time()

        result = mcp_client.call_tool("util_sleep", {"milliseconds": 100})

        elapsed = (time.time() - start) * 1000  # в миллисекундах

        assert result.success, f"util_sleep failed: {result.error}"
        assert elapsed >= 90, f"Sleep was too short: {elapsed}ms (expected >= 90ms)"
        assert elapsed < 500, f"Sleep was too long: {elapsed}ms (expected < 500ms)"

    def test_util_sleep_returns_success_status(self, mcp_client: MCPClient):
        """util_sleep возвращает статус success"""
        result = mcp_client.call_tool("util_sleep", {"milliseconds": 10})

        assert result.success
        assert result.content.get("status") == "success"

    def test_util_sleep_returns_message(self, mcp_client: MCPClient):
        """util_sleep возвращает сообщение с временем"""
        result = mcp_client.call_tool("util_sleep", {"milliseconds": 50})

        assert result.success
        assert "message" in result.content
        assert "50" in result.content["message"], "Message should contain sleep time"

    def test_util_sleep_zero_milliseconds(self, mcp_client: MCPClient):
        """util_sleep с 0ms работает корректно"""
        result = mcp_client.call_tool("util_sleep", {"milliseconds": 0})

        assert result.success

    def test_util_sleep_requires_milliseconds(self, mcp_client: MCPClient):
        """util_sleep требует параметр milliseconds"""
        result = mcp_client.call_tool("util_sleep", {})

        # Ожидаем ошибку или неуспешный результат
        assert (
            not result.success
            or "error" in str(result.content).lower()
            or "missing" in str(result.error).lower()
        )

    @pytest.mark.slow
    def test_util_sleep_500ms(self, mcp_client: MCPClient):
        """util_sleep с 500ms занимает примерно 500ms"""
        start = time.time()

        result = mcp_client.call_tool("util_sleep", {"milliseconds": 500})

        elapsed = (time.time() - start) * 1000

        assert result.success
        assert elapsed >= 450, f"Sleep was too short: {elapsed}ms"
        assert elapsed < 1000, f"Sleep was too long: {elapsed}ms"


class TestMCPServerBasics:
    """Базовые тесты MCP сервера"""

    def test_list_tools_returns_all_tools(self, mcp_client: MCPClient):
        """list_tools возвращает все 46 tools"""
        tools = mcp_client.list_tools()

        assert len(tools) >= 40, f"Expected at least 40 tools, got {len(tools)}"

        # Проверяем наличие некоторых ключевых tools
        tool_names = [t["name"] for t in tools]

        expected_tools = [
            "mouse_move",
            "mouse_click",
            "key_tap",
            "type_text",
            "screen_capture",
            "window_get_active",
            "process_list",
            "system_get_info",
            "util_sleep",
        ]

        for expected in expected_tools:
            assert expected in tool_names, f"Missing expected tool: {expected}"

    def test_tools_have_descriptions(self, mcp_client: MCPClient):
        """Все tools имеют описания"""
        tools = mcp_client.list_tools()

        for tool in tools:
            assert "name" in tool, f"Tool missing name: {tool}"
            assert "description" in tool, f"Tool {tool.get('name')} missing description"
            assert tool["description"], f"Tool {tool.get('name')} has empty description"

    def test_call_nonexistent_tool_fails(self, mcp_client: MCPClient):
        """Вызов несуществующего tool возвращает ошибку"""
        result = mcp_client.call_tool("nonexistent_tool_12345")

        # Ожидаем ошибку
        assert not result.success or "error" in str(result.raw_response).lower()
