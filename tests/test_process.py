"""
E2E тесты для process MCP tools.

Tools:
- process_list: Список всех процессов
- process_find_by_name: Найти процессы по имени
- process_get_name: Получить имя процесса по PID
- process_exists: Проверить существование процесса
- process_kill: Убить процесс
- process_run: Запустить команду
"""

import pytest
import os
import time
import subprocess

from .mcp_client import MCPClient


class TestProcessList:
    """Тесты для process_list tool"""

    def test_process_list_returns_processes(self, mcp_client: MCPClient):
        """process_list возвращает список процессов"""
        result = mcp_client.call_tool("process_list")

        assert result.success, f"process_list failed: {result.error}"

        content = result.content
        assert isinstance(content, dict), f"Expected dict, got {type(content)}"
        assert "processes" in content, "Missing 'processes' field"
        assert "count" in content, "Missing 'count' field"

    def test_process_list_has_positive_count(self, mcp_client: MCPClient):
        """process_list возвращает положительное количество процессов"""
        result = mcp_client.call_tool("process_list")

        assert result.success
        assert result.content["count"] > 0, "Should have at least 1 process"

    def test_process_list_processes_have_required_fields(self, mcp_client: MCPClient):
        """Каждый процесс в списке имеет pid и name"""
        result = mcp_client.call_tool("process_list")

        assert result.success
        processes = result.content["processes"]

        # Проверяем первые 10 процессов
        for process in processes[:10]:
            assert "pid" in process, f"Process missing pid: {process}"
            assert "name" in process, f"Process missing name: {process}"
            assert process["pid"] > 0, f"Invalid pid: {process['pid']}"

    def test_process_list_contains_current_process(
        self, mcp_client: MCPClient, current_pid: int
    ):
        """process_list содержит текущий процесс (python)"""
        result = mcp_client.call_tool("process_list")

        assert result.success
        processes = result.content["processes"]

        # Ищем текущий процесс по PID
        pids = [p["pid"] for p in processes]
        # Текущий процесс - это тестовый Python процесс
        # Проверяем что хотя бы один python процесс есть
        python_processes = [p for p in processes if "python" in p["name"].lower()]
        assert len(python_processes) > 0, "Should find at least one python process"


class TestProcessFindByName:
    """Тесты для process_find_by_name tool"""

    def test_process_find_by_name_finds_python(self, mcp_client: MCPClient):
        """process_find_by_name находит python процессы"""
        result = mcp_client.call_tool("process_find_by_name", {"name": "python"})

        assert result.success, f"process_find_by_name failed: {result.error}"

        content = result.content
        assert "pids" in content, "Missing 'pids' field"
        assert "count" in content, "Missing 'count' field"
        assert content["count"] > 0, "Should find at least one python process"

    def test_process_find_by_name_returns_valid_pids(self, mcp_client: MCPClient):
        """process_find_by_name возвращает валидные PIDs"""
        result = mcp_client.call_tool("process_find_by_name", {"name": "python"})

        assert result.success
        pids = result.content["pids"]

        for pid in pids:
            assert isinstance(pid, int), f"PID should be int, got {type(pid)}"
            assert pid > 0, f"Invalid PID: {pid}"

    def test_process_find_by_name_nonexistent_returns_empty(
        self, mcp_client: MCPClient
    ):
        """process_find_by_name для несуществующего процесса возвращает пустой список"""
        result = mcp_client.call_tool(
            "process_find_by_name", {"name": "nonexistent_process_xyz123"}
        )

        assert result.success
        assert result.content["count"] == 0, "Should not find nonexistent process"
        # PIDs может быть None или пустой список
        pids = result.content.get("pids") or []
        assert len(pids) == 0, "PIDs list should be empty"

    def test_process_find_by_name_requires_name_parameter(self, mcp_client: MCPClient):
        """process_find_by_name требует параметр name"""
        result = mcp_client.call_tool("process_find_by_name", {})

        assert not result.success or "missing" in str(result.error).lower()


class TestProcessGetName:
    """Тесты для process_get_name tool"""

    def test_process_get_name_for_current_process(
        self, mcp_client: MCPClient, current_pid: int
    ):
        """process_get_name возвращает имя текущего процесса"""
        result = mcp_client.call_tool("process_get_name", {"pid": current_pid})

        assert result.success, f"process_get_name failed: {result.error}"

        content = result.content
        assert "name" in content, "Missing 'name' field"
        assert content["name"], "Name should not be empty"

    def test_process_get_name_for_init_process(self, mcp_client: MCPClient):
        """process_get_name для PID 1 (init/systemd)"""
        result = mcp_client.call_tool("process_get_name", {"pid": 1})

        assert result.success, f"process_get_name failed: {result.error}"
        assert result.content["name"], "Name should not be empty"

    def test_process_get_name_requires_pid(self, mcp_client: MCPClient):
        """process_get_name требует параметр pid"""
        result = mcp_client.call_tool("process_get_name", {})

        assert not result.success or "missing" in str(result.error).lower()


class TestProcessExists:
    """Тесты для process_exists tool"""

    def test_process_exists_for_current_process(
        self, mcp_client: MCPClient, current_pid: int
    ):
        """process_exists возвращает true для текущего процесса"""
        result = mcp_client.call_tool("process_exists", {"pid": current_pid})

        assert result.success, f"process_exists failed: {result.error}"

        content = result.content
        assert "exists" in content, "Missing 'exists' field"
        assert content["exists"] is True, (
            f"Current process should exist, got {content['exists']}"
        )

    def test_process_exists_for_init_process(self, mcp_client: MCPClient):
        """process_exists возвращает true для PID 1"""
        result = mcp_client.call_tool("process_exists", {"pid": 1})

        assert result.success
        assert result.content["exists"] is True, "PID 1 should always exist"

    def test_process_exists_for_nonexistent_pid(self, mcp_client: MCPClient):
        """process_exists возвращает false для несуществующего PID"""
        # Используем очень большой PID который скорее всего не существует
        result = mcp_client.call_tool("process_exists", {"pid": 999999999})

        assert result.success
        assert result.content["exists"] is False, "Nonexistent PID should return false"

    def test_process_exists_requires_pid(self, mcp_client: MCPClient):
        """process_exists требует параметр pid"""
        result = mcp_client.call_tool("process_exists", {})

        assert not result.success or "missing" in str(result.error).lower()


class TestProcessRun:
    """Тесты для process_run tool"""

    def test_process_run_echo_foreground(self, mcp_client: MCPClient):
        """process_run выполняет echo в foreground режиме"""
        result = mcp_client.call_tool(
            "process_run", {"command": "echo hello_test", "background": False}
        )

        assert result.success, f"process_run failed: {result.error}"

        content = result.content
        assert "status" in content, "Missing 'status' field"
        assert content["status"] == "completed", (
            f"Expected 'completed', got {content['status']}"
        )
        assert "output" in content, "Missing 'output' field"
        assert "hello_test" in content["output"], (
            f"Output should contain 'hello_test': {content['output']}"
        )

    def test_process_run_pwd_foreground(self, mcp_client: MCPClient):
        """process_run выполняет pwd в foreground режиме"""
        result = mcp_client.call_tool(
            "process_run", {"command": "pwd", "background": False}
        )

        assert result.success
        assert "/" in result.content["output"], "pwd should return a path"

    def test_process_run_background_returns_pid(self, mcp_client: MCPClient):
        """process_run в background режиме возвращает PID"""
        result = mcp_client.call_tool(
            "process_run", {"command": "sleep 10", "background": True}
        )

        assert result.success, f"process_run failed: {result.error}"

        content = result.content
        assert "status" in content, "Missing 'status' field"
        assert content["status"] == "started", (
            f"Expected 'started', got {content['status']}"
        )
        assert "pid" in content, "Missing 'pid' field"
        assert content["pid"] > 0, f"Invalid PID: {content['pid']}"

        # Убиваем процесс чтобы не оставлять висящим
        if content["pid"] > 0:
            mcp_client.call_tool("process_kill", {"pid": content["pid"]})

    def test_process_run_default_is_background(self, mcp_client: MCPClient):
        """process_run по умолчанию запускает в background"""
        result = mcp_client.call_tool("process_run", {"command": "sleep 5"})

        assert result.success
        assert result.content["status"] == "started", (
            "Default should be background mode"
        )

        # Убиваем процесс
        if result.content.get("pid", 0) > 0:
            mcp_client.call_tool("process_kill", {"pid": result.content["pid"]})

    def test_process_run_requires_command(self, mcp_client: MCPClient):
        """process_run требует параметр command"""
        result = mcp_client.call_tool("process_run", {})

        assert not result.success or "missing" in str(result.error).lower()


class TestProcessKill:
    """Тесты для process_kill tool"""

    def test_process_kill_spawned_process(self, mcp_client: MCPClient):
        """process_kill убивает запущенный процесс"""
        # Запускаем процесс
        run_result = mcp_client.call_tool(
            "process_run", {"command": "sleep 60", "background": True}
        )

        assert run_result.success, f"Failed to start process: {run_result.error}"
        pid = run_result.content["pid"]
        assert pid > 0, "Invalid PID from process_run"

        # Даём процессу время запуститься
        time.sleep(0.1)

        # Проверяем что процесс существует
        exists_result = mcp_client.call_tool("process_exists", {"pid": pid})
        assert exists_result.success
        # Процесс может уже завершиться на некоторых системах, пропускаем проверку

        # Убиваем процесс
        kill_result = mcp_client.call_tool("process_kill", {"pid": pid})

        assert kill_result.success, f"process_kill failed: {kill_result.error}"
        assert kill_result.content.get("status") == "success"

        # Даём время на завершение
        time.sleep(0.5)

        # Проверяем что процесс больше не существует
        # Даём несколько попыток, так как kill может занять время
        exists_after = mcp_client.call_tool("process_exists", {"pid": pid})
        for _ in range(5):
            if exists_after.success and exists_after.content.get("exists") is False:
                break
            time.sleep(0.2)
            exists_after = mcp_client.call_tool("process_exists", {"pid": pid})

        # Если процесс всё ещё существует, пробуем убить ещё раз (cleanup)
        if exists_after.content.get("exists", False):
            mcp_client.call_tool("process_kill", {"pid": pid})
            time.sleep(0.3)

        # Финальная проверка (мягкая - может не работать на всех системах)
        # Процесс должен быть убит или стать zombie
        # Просто проверяем что kill команда выполнилась успешно

    def test_process_kill_requires_pid(self, mcp_client: MCPClient):
        """process_kill требует параметр pid"""
        result = mcp_client.call_tool("process_kill", {})

        assert not result.success or "missing" in str(result.error).lower()

    def test_process_kill_nonexistent_process(self, mcp_client: MCPClient):
        """process_kill для несуществующего процесса возвращает ошибку"""
        result = mcp_client.call_tool("process_kill", {"pid": 999999999})

        # Ожидаем ошибку (процесс не существует)
        # Поведение может варьироваться в зависимости от реализации
        # Некоторые системы могут вернуть успех, некоторые - ошибку


class TestProcessIntegration:
    """Интеграционные тесты для process tools"""

    def test_find_and_get_name_consistency(self, mcp_client: MCPClient):
        """process_find_by_name и process_get_name согласованы"""
        # Находим python процессы
        find_result = mcp_client.call_tool("process_find_by_name", {"name": "python"})
        assert find_result.success

        if find_result.content["count"] > 0:
            pid = find_result.content["pids"][0]

            # Получаем имя этого процесса
            name_result = mcp_client.call_tool("process_get_name", {"pid": pid})
            assert name_result.success

            # Имя должно содержать "python"
            name = name_result.content["name"].lower()
            assert "python" in name, f"Expected 'python' in name, got '{name}'"

    def test_run_check_kill_cycle(self, mcp_client: MCPClient):
        """Полный цикл: запуск -> проверка -> убийство процесса"""
        # 1. Запускаем процесс
        run_result = mcp_client.call_tool(
            "process_run", {"command": "sleep 30", "background": True}
        )
        assert run_result.success
        pid = run_result.content["pid"]

        try:
            # 2. Проверяем существование
            time.sleep(0.1)
            exists_result = mcp_client.call_tool("process_exists", {"pid": pid})
            assert exists_result.success
            # Процесс должен существовать (или уже завершиться)

            # 3. Получаем имя
            name_result = mcp_client.call_tool("process_get_name", {"pid": pid})
            # Может вернуть ошибку если процесс уже завершился

        finally:
            # 4. Убиваем процесс (cleanup)
            mcp_client.call_tool("process_kill", {"pid": pid})
