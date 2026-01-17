"""
MCP Client для взаимодействия с MCP сервером через stdio протокол.
Реализует JSON-RPC 2.0 поверх stdin/stdout (line-based).

Этот сервер использует простой line-based JSON-RPC:
- Каждый запрос - отдельная строка JSON
- Каждый ответ - отдельная строка JSON
"""

import subprocess
import json
import threading
import queue
import os
import time
from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class ToolResult:
    """Результат вызова MCP tool"""

    success: bool
    content: Any
    error: Optional[str] = None
    raw_response: Optional[dict] = None


class MCPClient:
    """
    MCP клиент для взаимодействия с сервером через stdio.

    Использование:
        with MCPClient("./go_computer_use_mcp_server") as client:
            result = client.call_tool("mouse_get_position")
            print(result.content)
    """

    def __init__(self, server_path: str, timeout: float = 30.0):
        """
        Args:
            server_path: Путь к исполняемому файлу MCP сервера
            timeout: Таймаут для операций в секундах
        """
        self.server_path = server_path
        self.timeout = timeout
        self.process: Optional[subprocess.Popen] = None
        self._request_id = 0
        self._response_queue: queue.Queue = queue.Queue()
        self._reader_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()
        self._initialized = False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False

    def start(self):
        """Запустить MCP сервер и инициализировать соединение"""
        if self.process is not None:
            return

        # Проверяем существование бинарника
        if not os.path.exists(self.server_path):
            raise FileNotFoundError(f"MCP server not found at: {self.server_path}")

        # Запускаем сервер
        self.process = subprocess.Popen(
            [self.server_path, "-t", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,  # Unbuffered
        )

        self._running = True

        # Запускаем поток чтения ответов
        self._reader_thread = threading.Thread(target=self._read_responses, daemon=True)
        self._reader_thread.start()

        # Ждём небольшую паузу для запуска сервера
        time.sleep(0.2)

        # Инициализируем MCP соединение
        self._initialize()

    def stop(self):
        """Остановить MCP сервер"""
        self._running = False

        if self.process:
            try:
                self.process.stdin.close()
                self.process.terminate()
                self.process.wait(timeout=5)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            finally:
                self.process = None

        self._initialized = False

    def _next_id(self) -> int:
        """Получить следующий ID запроса"""
        with self._lock:
            self._request_id += 1
            return self._request_id

    def _send_request(self, method: str, params: Optional[dict] = None) -> dict:
        """
        Отправить JSON-RPC запрос и получить ответ.

        Args:
            method: Название метода
            params: Параметры запроса

        Returns:
            JSON-RPC ответ
        """
        if not self.process or self.process.poll() is not None:
            raise RuntimeError("MCP server is not running")

        request_id = self._next_id()

        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
        }

        if params is not None:
            request["params"] = params

        # Сериализуем запрос (line-based JSON-RPC)
        body = json.dumps(request) + "\n"

        # Отправляем
        try:
            self.process.stdin.write(body.encode("utf-8"))
            self.process.stdin.flush()
        except BrokenPipeError:
            raise RuntimeError("MCP server connection closed")

        # Ждём ответ
        try:
            response = self._response_queue.get(timeout=self.timeout)
            return response
        except queue.Empty:
            raise TimeoutError(f"Timeout waiting for response to {method}")

    def _read_responses(self):
        """Фоновый поток для чтения ответов от сервера"""
        while self._running and self.process and self.process.poll() is None:
            try:
                response = self._read_message()
                if response:
                    self._response_queue.put(response)
            except Exception as e:
                if self._running:
                    # Продолжаем при ошибках
                    pass

    def _read_message(self) -> Optional[dict]:
        """Прочитать одно JSON-RPC сообщение (line-based)"""
        if not self.process or not self.process.stdout:
            return None

        try:
            line = self.process.stdout.readline()
            if not line:
                return None

            line = line.decode("utf-8").strip()

            if not line:
                return None

            # Парсим JSON
            return json.loads(line)

        except json.JSONDecodeError:
            return None
        except Exception:
            return None

    def _initialize(self):
        """Инициализировать MCP соединение"""
        response = self._send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "mcp-e2e-test-client", "version": "1.0.0"},
            },
        )

        if "error" in response:
            raise RuntimeError(f"Failed to initialize MCP: {response['error']}")

        # Отправляем notifications/initialized
        notification = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        body = json.dumps(notification) + "\n"
        self.process.stdin.write(body.encode("utf-8"))
        self.process.stdin.flush()

        self._initialized = True

        return response.get("result", {})

    def list_tools(self) -> list:
        """
        Получить список доступных tools.

        Returns:
            Список словарей с информацией о tools
        """
        response = self._send_request("tools/list")

        if "error" in response:
            raise RuntimeError(f"Failed to list tools: {response['error']}")

        return response.get("result", {}).get("tools", [])

    def call_tool(self, name: str, arguments: Optional[dict] = None) -> ToolResult:
        """
        Вызвать MCP tool.

        Args:
            name: Название tool
            arguments: Аргументы для tool

        Returns:
            ToolResult с результатом вызова
        """
        response = self._send_request(
            "tools/call", {"name": name, "arguments": arguments or {}}
        )

        if "error" in response:
            return ToolResult(
                success=False,
                content=None,
                error=str(response["error"]),
                raw_response=response,
            )

        result = response.get("result", {})
        content = result.get("content", [])

        # Парсим content
        parsed_content = []
        for item in content:
            if item.get("type") == "text":
                text = item.get("text", "")
                try:
                    # Пробуем распарсить как JSON
                    parsed_content.append(json.loads(text))
                except json.JSONDecodeError:
                    parsed_content.append(text)
            elif item.get("type") == "image":
                parsed_content.append(
                    {
                        "type": "image",
                        "data": item.get("data", ""),
                        "mimeType": item.get("mimeType", "image/png"),
                    }
                )
            else:
                parsed_content.append(item)

        # Если только один элемент, возвращаем его напрямую
        final_content = (
            parsed_content[0] if len(parsed_content) == 1 else parsed_content
        )

        return ToolResult(
            success=True, content=final_content, error=None, raw_response=response
        )

    def call_tool_raw(self, name: str, arguments: Optional[dict] = None) -> dict:
        """
        Вызвать MCP tool и получить сырой ответ.

        Args:
            name: Название tool
            arguments: Аргументы для tool

        Returns:
            Сырой JSON-RPC ответ
        """
        return self._send_request(
            "tools/call", {"name": name, "arguments": arguments or {}}
        )


# Вспомогательные функции для упрощения тестов
def get_default_server_path() -> str:
    """Получить путь к MCP серверу по умолчанию"""
    # Определяем путь относительно этого файла
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(tests_dir)
    return os.path.join(project_dir, "go_computer_use_mcp_server")


if __name__ == "__main__":
    # Простой тест клиента
    server_path = get_default_server_path()
    print(f"Testing MCP client with server: {server_path}")

    with MCPClient(server_path) as client:
        # Список tools
        tools = client.list_tools()
        print(f"Available tools: {len(tools)}")
        for tool in tools[:5]:
            print(f"  - {tool['name']}: {tool.get('description', '')[:50]}...")

        # Тест простого tool
        result = client.call_tool("mouse_get_position")
        print(f"\nmouse_get_position: {result.content}")

        result = client.call_tool("screen_get_size")
        print(f"screen_get_size: {result.content}")

        result = client.call_tool("system_get_info")
        print(f"system_get_info: {result.content}")
