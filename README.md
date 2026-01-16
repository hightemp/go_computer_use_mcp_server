# go_computer_use_mcp_server

MCP (Model Context Protocol) server in Go for computer automation. Uses [robotgo](https://github.com/hightemp/robotgo) library for desktop automation.

## Features

- **Mouse control**: movement, clicks, dragging, scrolling
- **Keyboard control**: key presses, text input, hotkeys
- **Screen operations**: screenshots, pixel color, display information
- **Window management**: move, resize, minimize/maximize
- **Process management**: list processes, search, terminate
- **System utilities**: system info, dialogs, delays

## Quick Start with npx

The easiest way to run the server is via npx (requires Node.js 18+):

```bash
# Run with stdio transport (for MCP clients)
npx go-computer-use-mcp-server -t stdio

# Run with SSE transport
npx go-computer-use-mcp-server -t sse -h 0.0.0.0 -p 8080
```

## Integration with AI Tools

### Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "computer-use": {
      "command": "npx",
      "args": ["-y", "go-computer-use-mcp-server", "-t", "stdio"]
    }
  }
}
```

### Claude Code (claude-code CLI)

```bash
claude mcp add computer-use -- npx -y go-computer-use-mcp-server -t stdio
```

Or add manually to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "computer-use": {
      "command": "npx",
      "args": ["-y", "go-computer-use-mcp-server", "-t", "stdio"]
    }
  }
}
```

### OpenCode

Add to your `opencode.json` configuration:

```json
{
  "mcp": {
    "servers": {
      "computer-use": {
        "command": "npx",
        "args": ["-y", "go-computer-use-mcp-server", "-t", "stdio"]
      }
    }
  }
}
```

### Codex (OpenAI)

Add to your Codex MCP configuration:

```json
{
  "mcpServers": {
    "computer-use": {
      "command": "npx",
      "args": ["-y", "go-computer-use-mcp-server", "-t", "stdio"]
    }
  }
}
```

### Cursor

Add to your Cursor settings (Settings > MCP Servers):

```json
{
  "mcpServers": {
    "computer-use": {
      "command": "npx",
      "args": ["-y", "go-computer-use-mcp-server", "-t", "stdio"]
    }
  }
}
```

### Windsurf

Add to your Windsurf MCP configuration:

```json
{
  "mcpServers": {
    "computer-use": {
      "command": "npx",
      "args": ["-y", "go-computer-use-mcp-server", "-t", "stdio"]
    }
  }
}
```

### Cline (VS Code Extension)

Add to Cline MCP settings in VS Code:

```json
{
  "mcpServers": {
    "computer-use": {
      "command": "npx",
      "args": ["-y", "go-computer-use-mcp-server", "-t", "stdio"]
    }
  }
}
```

### Generic MCP Client

For any MCP-compatible client, use:

```bash
npx -y go-computer-use-mcp-server -t stdio
```

## Installation from Source

### Requirements

- Go 1.21+
- GCC compiler
- X11 libraries (Linux)

### Ubuntu/Debian

```bash
# Go (if not installed)
sudo snap install go --classic

# GCC
sudo apt install gcc libc6-dev

# X11
sudo apt install libx11-dev xorg-dev libxtst-dev

# Clipboard support
sudo apt install xsel xclip

# Bitmap support (for image operations)
sudo apt install libpng++-dev

# Event hook support
sudo apt install xcb libxcb-xkb-dev x11-xkb-utils libx11-xcb-dev libxkbcommon-x11-dev libxkbcommon-dev
```

**One-liner:**
```bash
sudo apt install gcc libc6-dev libx11-dev xorg-dev libxtst-dev xsel xclip libpng++-dev xcb libxcb-xkb-dev x11-xkb-utils libx11-xcb-dev libxkbcommon-x11-dev libxkbcommon-dev
```

### Fedora

```bash
# GCC (if not installed)
sudo dnf install gcc

# X11
sudo dnf install libX11-devel libXtst-devel

# Clipboard support
sudo dnf install xsel xclip

# Bitmap support
sudo dnf install libpng-devel

# Event hook support
sudo dnf install libxkbcommon-devel libxkbcommon-x11-devel xorg-x11-xkb-utils-devel
```

**One-liner:**
```bash
sudo dnf install gcc libX11-devel libXtst-devel xsel xclip libpng-devel libxkbcommon-devel libxkbcommon-x11-devel xorg-x11-xkb-utils-devel
```

### Build

```bash
# Download dependencies
make deps

# Build for current platform
make build

# Build for all platforms
make build-all
```

## Running (from source)

### SSE transport (default)

```bash
./go_computer_use_mcp_server -t sse -h 0.0.0.0 -p 8080
```

### Stdio transport

```bash
./go_computer_use_mcp_server -t stdio
```

### Command line arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `-t` | Transport: `sse` or `stdio` | `sse` |
| `-h` | Host for SSE server | `0.0.0.0` |
| `-p` | Port for SSE server | `8080` |

## Available Tools

### Mouse Control (12 tools)

| Tool | Description |
|------|-------------|
| `mouse_move` | Move cursor to absolute coordinates |
| `mouse_move_smooth` | Smooth cursor movement (human-like) |
| `mouse_move_relative` | Relative cursor movement |
| `mouse_get_position` | Get current cursor position |
| `mouse_click` | Mouse click |
| `mouse_click_at` | Move and click |
| `mouse_toggle` | Press/release mouse button |
| `mouse_drag` | Drag operation |
| `mouse_drag_smooth` | Smooth drag operation |
| `mouse_scroll` | Scroll |
| `mouse_scroll_direction` | Scroll in direction |
| `mouse_scroll_smooth` | Smooth scroll |

### Keyboard Control (7 tools)

| Tool | Description |
|------|-------------|
| `key_tap` | Key press (with modifiers) |
| `key_toggle` | Press/release key |
| `type_text` | Type text (UTF-8) |
| `type_text_delayed` | Type text with delay |
| `clipboard_read` | Read clipboard |
| `clipboard_write` | Write to clipboard |
| `clipboard_paste` | Paste via clipboard |

### Screen Operations (7 tools)

| Tool | Description |
|------|-------------|
| `screen_get_size` | Get screen size |
| `screen_get_displays_num` | Number of monitors |
| `screen_get_display_bounds` | Monitor bounds |
| `screen_capture` | Screen capture (returns MCP ImageContent) |
| `screen_capture_save` | Capture and save to file |
| `screen_get_pixel_color` | Pixel color at coordinates |
| `screen_get_mouse_color` | Pixel color under cursor |

### Window Management (9 tools)

| Tool | Description |
|------|-------------|
| `window_get_active` | Active window information |
| `window_get_title` | Window title |
| `window_get_bounds` | Window bounds |
| `window_set_active` | Activate window |
| `window_move` | Move window |
| `window_resize` | Resize window |
| `window_minimize` | Minimize window |
| `window_maximize` | Maximize window |
| `window_close` | Close window |

### Process Management (6 tools)

| Tool | Description |
|------|-------------|
| `process_list` | List all processes |
| `process_find_by_name` | Find processes by name |
| `process_get_name` | Get process name by PID |
| `process_exists` | Check if process exists |
| `process_kill` | Kill process |
| `process_run` | Run command |

### System Utilities (3 tools)

| Tool | Description |
|------|-------------|
| `system_get_info` | System information |
| `util_sleep` | Sleep/delay |
| `alert_show` | Show dialog |

## Usage Examples

### Move mouse and click

```json
{
  "tool": "mouse_click_at",
  "arguments": {
    "x": 100,
    "y": 200,
    "button": "left",
    "double": false
  }
}
```

### Type text

```json
{
  "tool": "type_text",
  "arguments": {
    "text": "Hello, World!",
    "delay": 50
  }
}
```

### Hotkeys

```json
{
  "tool": "key_tap",
  "arguments": {
    "key": "c",
    "modifiers": ["ctrl"]
  }
}
```

### Screen capture

```json
{
  "tool": "screen_capture",
  "arguments": {
    "x": 0,
    "y": 0,
    "width": 800,
    "height": 600
  }
}
```

## Supported Keys

### Letters and numbers
`a-z`, `A-Z`, `0-9`

### Function keys
`f1`-`f24`

### Navigation
`up`, `down`, `left`, `right`, `home`, `end`, `pageup`, `pagedown`

### Special keys
`backspace`, `delete`, `enter`, `tab`, `escape`, `space`, `insert`, `capslock`

### Modifiers
`alt`, `ctrl`, `shift`, `cmd` (or `command`)

### Multimedia
`audio_mute`, `audio_vol_down`, `audio_vol_up`, `audio_play`, `audio_stop`, `audio_pause`

## License

MIT
