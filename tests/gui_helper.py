"""
Tkinter тестовое окно для E2E тестирования MCP сервера.

Запускается как отдельный процесс для избежания проблем с многопоточностью Tkinter.
"""

import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import subprocess
import sys
import os
import time
import json
import tempfile
from typing import Optional, Tuple
from dataclasses import dataclass, field


# Скрипт для запуска окна в отдельном процессе
WINDOW_SCRIPT = """
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import sys
import json
import time

class TestWindowApp:
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    
    def __init__(self, state_file):
        self.state_file = state_file
        self.root = tk.Tk()
        self.root.title("MCP E2E Test Window")
        self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+100+100")
        self.root.resizable(False, False)
        
        self.button_clicks = []
        self.entry = None
        self.entry2 = None
        
        self._setup_window()
        self._write_state()
        
    def _setup_window(self):
        self.canvas = tk.Canvas(self.root, width=self.WINDOW_WIDTH, height=self.WINDOW_HEIGHT, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Красный квадрат (50,50 - 150,150)
        self.canvas.create_rectangle(50, 50, 150, 150, fill="red", outline="darkred", width=2)
        
        # Синий круг (200,50 - 300,150)
        self.canvas.create_oval(200, 50, 300, 150, fill="blue", outline="darkblue", width=2)
        
        # Зелёный квадрат (350,50 - 450,150)
        self.canvas.create_rectangle(350, 50, 450, 150, fill="green", outline="darkgreen", width=2)
        
        # Метки цветов
        self.canvas.create_text(100, 165, text="RED")
        self.canvas.create_text(250, 165, text="BLUE")
        self.canvas.create_text(400, 165, text="GREEN")
        
        # Button 1
        self.button1 = tk.Button(self.root, text="Button 1", command=lambda: self._on_click("button1"), width=15)
        self.canvas.create_window(150, 200, window=self.button1)
        
        # Button 2
        self.button2 = tk.Button(self.root, text="Button 2", command=lambda: self._on_click("button2"), width=15)
        self.canvas.create_window(400, 200, window=self.button2)
        
        # Entry
        self.canvas.create_text(100, 280, text="Text Input:", anchor="w")
        self.entry = tk.Entry(self.root, width=50, font=("Arial", 12))
        self.canvas.create_window(300, 300, window=self.entry)
        
        # Entry 2
        self.canvas.create_text(100, 340, text="Paste Here:", anchor="w")
        self.entry2 = tk.Entry(self.root, width=50, font=("Arial", 12))
        self.canvas.create_window(300, 360, window=self.entry2)
        
        # Scrollable text
        frame = tk.Frame(self.root, width=300, height=100)
        self.canvas.create_window(600, 500, window=frame)
        self.scrolled_text = ScrolledText(frame, width=35, height=5)
        self.scrolled_text.pack(fill=tk.BOTH, expand=True)
        for i in range(50):
            self.scrolled_text.insert(tk.END, f"Line {i+1}: Test line for scrolling.\\n")
        
        # Периодически обновляем состояние
        self.root.after(100, self._periodic_update)
        
    def _on_click(self, name):
        self.button_clicks.append(name)
        self._write_state()
        
    def _periodic_update(self):
        self._write_state()
        self.root.after(100, self._periodic_update)
        
    def _write_state(self):
        state = {
            "x": self.root.winfo_x(),
            "y": self.root.winfo_y(),
            "width": self.root.winfo_width(),
            "height": self.root.winfo_height(),
            "button_clicks": self.button_clicks,
            "entry_text": self.entry.get() if self.entry else "",
            "entry2_text": self.entry2.get() if self.entry2 else "",
            "ready": True
        }
        try:
            with open(self.state_file, "w") as f:
                json.dump(state, f)
        except:
            pass
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    state_file = sys.argv[1]
    app = TestWindowApp(state_file)
    app.run()
"""


@dataclass
class WindowState:
    """Состояние тестового окна"""

    x: int = 100
    y: int = 100
    width: int = 800
    height: int = 600
    button_clicks: list = field(default_factory=list)
    entry_text: str = ""
    entry2_text: str = ""
    ready: bool = False


class _GUIWindowHelper:
    """
    Тестовое окно, запускаемое как отдельный процесс.
    """

    WINDOW_X = 100
    WINDOW_Y = 100
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600

    RED_RECT = (50, 50, 150, 150)
    BLUE_CIRCLE = (200, 50, 300, 150)
    GREEN_RECT = (350, 50, 450, 150)

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self._state_file: Optional[str] = None
        self._script_file: Optional[str] = None
        self._state = WindowState()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False

    def start(self, timeout: float = 5.0):
        """Запустить тестовое окно как отдельный процесс"""
        if self.process is not None:
            return

        # Создаём временные файлы
        self._state_file = tempfile.mktemp(suffix=".json", prefix="mcp_test_window_")
        self._script_file = tempfile.mktemp(
            suffix=".py", prefix="mcp_test_window_script_"
        )

        # Записываем скрипт
        with open(self._script_file, "w") as f:
            f.write(WINDOW_SCRIPT)

        # Записываем начальное состояние
        with open(self._state_file, "w") as f:
            json.dump({"ready": False}, f)

        # Запускаем процесс
        self.process = subprocess.Popen(
            [sys.executable, self._script_file, self._state_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Ждём готовности
        start = time.time()
        while time.time() - start < timeout:
            self._read_state()
            if self._state.ready:
                time.sleep(0.2)  # Дополнительная пауза для стабилизации
                return
            time.sleep(0.1)

        raise TimeoutError("Test window failed to start")

    def stop(self):
        """Остановить тестовое окно"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            self.process = None

        # Удаляем временные файлы
        for path in [self._state_file, self._script_file]:
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except Exception:
                    pass

        self._state_file = None
        self._script_file = None

    def _read_state(self):
        """Прочитать состояние из файла"""
        if not self._state_file or not os.path.exists(self._state_file):
            return

        try:
            with open(self._state_file, "r") as f:
                data = json.load(f)
                self._state = WindowState(
                    x=data.get("x", 100),
                    y=data.get("y", 100),
                    width=data.get("width", 800),
                    height=data.get("height", 600),
                    button_clicks=data.get("button_clicks", []),
                    entry_text=data.get("entry_text", ""),
                    entry2_text=data.get("entry2_text", ""),
                    ready=data.get("ready", False),
                )
        except Exception:
            pass

    @property
    def state(self):
        """Текущее состояние окна"""
        self._read_state()
        return self._state

    def get_window_position(self) -> Tuple[int, int]:
        """Получить позицию окна"""
        self._read_state()
        return (self._state.x, self._state.y)

    def get_window_size(self) -> Tuple[int, int]:
        """Получить размер окна"""
        self._read_state()
        return (self._state.width, self._state.height)

    def get_absolute_coords(self, rel_x: int, rel_y: int) -> Tuple[int, int]:
        """Преобразовать относительные координаты в абсолютные"""
        win_x, win_y = self.get_window_position()
        return (win_x + rel_x, win_y + rel_y)

    def get_red_rect_center(self) -> Tuple[int, int]:
        """Центр красного квадрата"""
        center_x = (self.RED_RECT[0] + self.RED_RECT[2]) // 2
        center_y = (self.RED_RECT[1] + self.RED_RECT[3]) // 2
        return self.get_absolute_coords(center_x, center_y)

    def get_blue_circle_center(self) -> Tuple[int, int]:
        """Центр синего круга"""
        center_x = (self.BLUE_CIRCLE[0] + self.BLUE_CIRCLE[2]) // 2
        center_y = (self.BLUE_CIRCLE[1] + self.BLUE_CIRCLE[3]) // 2
        return self.get_absolute_coords(center_x, center_y)

    def get_green_rect_center(self) -> Tuple[int, int]:
        """Центр зелёного квадрата"""
        center_x = (self.GREEN_RECT[0] + self.GREEN_RECT[2]) // 2
        center_y = (self.GREEN_RECT[1] + self.GREEN_RECT[3]) // 2
        return self.get_absolute_coords(center_x, center_y)

    def get_button1_center(self) -> Tuple[int, int]:
        """Центр Button 1"""
        return self.get_absolute_coords(150, 200)

    def get_button2_center(self) -> Tuple[int, int]:
        """Центр Button 2"""
        return self.get_absolute_coords(400, 200)

    def get_entry_center(self) -> Tuple[int, int]:
        """Центр текстового поля"""
        return self.get_absolute_coords(300, 300)

    def get_entry2_center(self) -> Tuple[int, int]:
        """Центр второго текстового поля"""
        return self.get_absolute_coords(300, 360)

    def get_draggable_center(self) -> Tuple[int, int]:
        """Центр перетаскиваемой области"""
        return self.get_absolute_coords(350, 400)

    def get_scrolled_text_center(self) -> Tuple[int, int]:
        """Центр scrollable текста"""
        return self.get_absolute_coords(600, 500)

    def get_entry_text(self) -> str:
        """Текст из entry"""
        self._read_state()
        return self._state.entry_text

    def get_entry2_text(self) -> str:
        """Текст из entry2"""
        self._read_state()
        return self._state.entry2_text

    def clear_entry(self):
        """Очистить entry (через симуляцию Ctrl+A, Delete)"""
        # Это нужно делать через MCP tools, а не напрямую
        pass

    def clear_entry2(self):
        """Очистить entry2"""
        pass

    def clear_state(self):
        """Очистить состояние"""
        self._state.button_clicks.clear()

    def focus_entry(self):
        """Установить фокус на entry"""
        pass

    def focus_entry2(self):
        """Установить фокус на entry2"""
        pass

    def update(self):
        """Обновить состояние"""
        self._read_state()

    def get_scroll_position(self) -> float:
        """Позиция прокрутки"""
        return 0.0

    def get_pid(self) -> Optional[int]:
        """PID процесса окна"""
        if self.process:
            return self.process.pid
        return None

    def get_wm_state(self) -> str:
        """Состояние окна"""
        return "normal"


if __name__ == "__main__":
    print("Starting test window...")

    with _GUIWindowHelper() as window:
        print(f"Window position: {window.get_window_position()}")
        print(f"Window size: {window.get_window_size()}")
        print(f"Red rect center: {window.get_red_rect_center()}")
        print(f"Button 1 center: {window.get_button1_center()}")
        print(f"PID: {window.get_pid()}")

        input("Press Enter to close...")
