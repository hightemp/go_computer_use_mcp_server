---
name: desktop-automation
description: Patterns, gotchas, and best practices for cross-platform desktop automation with robotgo in Go. Covers display requirements, mouse/keyboard APIs, screenshot handling, window management, multi-monitor support, CGO, X11 specifics, and testing headless environments. Use when implementing or debugging robotgo-based tools, handling display errors, working with screen coordinates, or setting up headless CI testing.
argument-hint: '[topic: mouse|keyboard|screen|windows|display|ocr|testing|ci]'
allowed-tools: Read Grep Glob Write Bash(go build *) Bash(go run *) Bash(go test *) Bash(Xvfb *) Bash(DISPLAY=*) Bash(xdotool *)
metadata:
  author: aif
  version: "1.0"
  category: desktop-automation
---

# Desktop Automation Patterns (robotgo + Go)

## Library Overview

This project uses a **custom fork**: `github.com/hightemp/robotgo` (not the upstream `go-vgo/robotgo`).
The fork adds extra APIs and fixes. Always import from `github.com/hightemp/robotgo`.

```go
import "github.com/hightemp/robotgo"
```

---

## Display Requirements (X11/Linux)

robotgo requires an X11 display on Linux. Without `DISPLAY`, calls to robotgo will **segfault or panic**.

### Checking display availability
```go
// Safe display check pattern (see main.go)
display := os.Getenv("DISPLAY")
if display == "" {
    return fmt.Errorf("DISPLAY environment variable not set")
}

// Attempt a safe call to detect panics
func() {
    defer func() {
        if r := recover(); r != nil {
            displayAvailable = false
        }
    }()
    _, _ = robotgo.GetScreenSize()
    displayAvailable = true
}()
```

### Headless environments
Use [Xvfb](https://www.x.org/releases/X11R7.6/doc/man/man1/Xvfb.1.xhtml) for CI or Docker:
```bash
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
```
Or with `xvfb-run`:
```bash
xvfb-run -a ./go_computer_use_mcp_server -t stdio
```

### Running MCP server with display
```bash
# Pass DISPLAY through to the server process
DISPLAY=:0 XAUTHORITY=~/.Xauthority ./go_computer_use_mcp_server -t stdio
```

---

## Mouse API

```go
// Absolute move
robotgo.Move(x, y)
robotgo.Move(x, y, displayID)  // multi-monitor

// Smooth move (human-like, slower)
robotgo.MoveSmooth(x, y, low, high)  // low/high = speed range

// Relative move
robotgo.MoveRelative(dx, dy)

// Get position
x, y := robotgo.Location()

// Click: button = "left" | "right" | "center"
robotgo.Click(button)
robotgo.Click(button, true)  // double click

// Move + click in one call
robotgo.MoveClick(x, y, button)
robotgo.MoveClick(x, y, button, true)  // double

// Mouse button hold/release
robotgo.Toggle(button, "down")
robotgo.Toggle(button, "up")

// Drag to position
robotgo.Drag(x, y, button)

// Scroll: x, y = position, scrollX, scrollY = amount
robotgo.Scroll(x, y, scrollX, scrollY)
```

**Smooth drag pattern** (robotgo doesn't have built-in smooth drag with button selection):
```go
robotgo.Toggle(button, "down")
robotgo.MilliSleep(50)
robotgo.MoveSmooth(targetX, targetY, low, high)
robotgo.Toggle(button, "up")
```

---

## Keyboard API

```go
// Type a string (appropriate for text input)
robotgo.TypeStr("hello world")

// Press a key (by name)
robotgo.KeyTap("enter")
robotgo.KeyTap("tab")
robotgo.KeyTap("f5")
robotgo.KeyTap("a", "ctrl")         // Ctrl+A
robotgo.KeyTap("c", "ctrl")         // Ctrl+C
robotgo.KeyTap("z", "ctrl", "shift") // Ctrl+Shift+Z

// Hold / release a key
robotgo.KeyToggle("shift", "down")
robotgo.KeyToggle("shift", "up")

// Type with modifier held
robotgo.KeyToggle("shift", "down")
robotgo.TypeStr("UPPER")
robotgo.KeyToggle("shift", "up")
```

### Common key names
`enter`, `tab`, `space`, `backspace`, `delete`, `escape`, `up`, `down`, `left`, `right`,
`home`, `end`, `pageup`, `pagedown`, `f1`–`f12`,
`ctrl`, `alt`, `shift`, `cmd` (macOS `⌘`), `win` (Windows key)

---

## Screen / Screenshot API

```go
// Screen dimensions
width, height := robotgo.GetScreenSize()

// Number of screens
count := robotgo.ScaleF()  // NOTE: use GetScreenSize for display count

// Screenshot full screen → image.Image
img := robotgo.CaptureScreen()

// Screenshot region
img = robotgo.CaptureScreen(x, y, width, height)

// Convert to PNG bytes
var buf bytes.Buffer
png.Encode(&buf, img)
pngBytes := buf.Bytes()

// Base64 for JSON transport
encoded := base64.StdEncoding.EncodeToString(pngBytes)

// Get pixel color at coordinate
color := robotgo.GetPixelColor(x, y)  // returns hex string e.g. "ff0000"
```

### Screenshot response pattern (used in this project)
```go
imgBytes := robotgo.CaptureScreen(x, y, w, h)
var buf bytes.Buffer
if err := png.Encode(&buf, imgBytes); err != nil {
    return nil, fmt.Errorf("failed to encode screenshot: %w", err)
}
return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
    "status": "success",
    "image":  base64.StdEncoding.EncodeToString(buf.Bytes()),
    "format": "png",
    "width":  w, "height": h,
})), nil
```

---

## Window Management API

```go
// Get all windows (returns []robotgo.Window or similar)
windows := robotgo.GetAllWindows()

// Active window
active := robotgo.GetActive()
title := robotgo.GetTitle(active)

// Find window by title
hwnd := robotgo.FindWindow("Firefox")

// Window operations
robotgo.SetActive(hwnd)
robotgo.MoveWindow(hwnd, x, y)
robotgo.ResizeWindow(hwnd, width, height)
robotgo.MinWindow(hwnd, true)   // minimize
robotgo.MaxWindow(hwnd, true)   // maximize
robotgo.CloseWindow(hwnd)
```

**Note:** Window APIs behave differently per OS. Test on Linux/X11, macOS, and Windows separately.

---

## Process Management

```go
// Using gopsutil (separate from robotgo)
import "github.com/shirou/gopsutil/v4/process"

procs, err := process.Processes()
for _, p := range procs {
    name, _ := p.Name()
    pid := p.Pid
    status, _ := p.Status()
}

// Kill process
p.Kill()
```

---

## Multi-Monitor Support

```go
// Move mouse to secondary display
robotgo.Move(x, y, displayID)  // displayID: 0 = primary

// Get display count and sizes
// Use gopsutil or xrandr command to enumerate displays on Linux
```

---

## OCR (via gosseract)

```go
import "github.com/otiai10/gosseract/v2"

// Basic usage
client := gosseract.NewClient()
defer client.Close()

// Set image from file or bytes
client.SetImageFromBytes(pngBytes)
text, err := client.Text()
```

**Requirements on Linux:** `tesseract-ocr` and language packs must be installed:
```bash
apt-get install tesseract-ocr tesseract-ocr-eng
```

---

## Common Gotchas

| Gotcha | Details |
|--------|---------|
| **Segfault without display** | Any robotgo call without X11 display will segfault. Always use `withDisplayCheck`. |
| **CGO required** | Cannot build with `CGO_ENABLED=0`. All CI runners need GCC. |
| **Screenshot on multi-monitor** | `CaptureScreen()` captures display 0 by default. Pass region if user specifies a monitor. |
| **Key names are OS-dependent** | `cmd` works on macOS, `ctrl` on Linux/Windows. Use runtime checks if needed. |
| **`TypeStr` vs `KeyTap`** | `TypeStr` is for text input; `KeyTap` is for control keys and shortcuts. Don't use `TypeStr` for `"enter"`. |
| **Mouse coord origin** | (0, 0) is always top-left of the primary monitor. Negative coords can refer to secondary monitors. |
| **`Toggle` return value** | Older robotgo returns `interface{}` from `Toggle`. Discarding with `_ =` is fine. |
| **Smooth drag with button** | robotgo's `DragSmooth` may ignore the button parameter — implement manually with `Toggle + MoveSmooth`. |
| **gosseract client lifecycle** | Always `defer client.Close()` — leaks if not closed. |

---

## Testing Strategy

### Unit tests
Not practical for robotgo calls (require display). Focus on:
- Argument parsing helpers
- JSON response formatting
- Error handling paths

### Integration tests (Python pytest — `tests/`)
```python
# tests/conftest.py starts the server subprocess
# tests/mcp_client.py provides call_tool() helper

def test_mouse_move(mcp_client):
    result = mcp_client.call_tool("mouse_move", {"x": 100, "y": 200})
    assert result["status"] == "success"
```

### Headless CI
```yaml
# .github/workflows/test.yml
- name: Install Xvfb
  run: sudo apt-get install -y xvfb

- name: Run tests
  run: |
    Xvfb :99 -screen 0 1920x1080x24 &
    export DISPLAY=:99
    make test
```

### Skipping GUI tests
```python
# tests/conftest.py
import pytest, os
no_display = os.environ.get("DISPLAY") == ""
skip_gui = pytest.mark.skipif(no_display, reason="No display available")
```

---

## Build Requirements

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install -y \
  gcc \
  libx11-dev \
  libxtst-dev \
  libxkbcommon-dev \
  xdotool \
  tesseract-ocr \
  tesseract-ocr-eng
```

### macOS
```bash
brew install tesseract
# Xcode command line tools for CGO
xcode-select --install
```

### Windows
- MinGW-w64 for CGO cross-compilation
- Tesseract installer from GitHub releases

---

## xdotool Integration

The server exposes an `xdotool` passthrough tool for advanced X11 operations not covered by robotgo:
```go
cmd := exec.Command("xdotool", args...)
output, err := cmd.CombinedOutput()
```
This is Linux/X11 only. Return an error or skip on other platforms.
