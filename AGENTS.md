# AGENTS.md

> Project map for AI agents. Keep this file up-to-date as the project evolves.

## Project Overview

`go_computer_use_mcp_server` is a Go-based MCP (Model Context Protocol) server that exposes comprehensive desktop automation capabilities — mouse, keyboard, screen, window management, process control, and OCR — to AI agents. Distributed as an npm package (`go-computer-use-mcp-server`) so clients can run it with a single `npx` command.

## Tech Stack

- **Language:** Go 1.24 (CGO required)
- **MCP Framework:** `github.com/mark3labs/mcp-go`
- **Desktop Automation:** `github.com/hightemp/robotgo` (X11/Windows/macOS)
- **OCR:** `github.com/otiai10/gosseract/v2` (Tesseract)
- **System Info:** `github.com/shirou/gopsutil/v4`
- **Transport:** Stdio (default) + SSE (HTTP)
- **Distribution:** npm wrapper (`package.json` + `bin/computer-use-mcp.js`)
- **Tests:** Python pytest (`tests/`)

## Project Structure

```
go_computer_use_mcp_server/
│
├── main.go                    # ALL server code — handlers, registration, bootstrap (~1500 lines)
├── go.mod                     # Go module definition and dependencies
├── go.sum                     # Dependency checksums
├── Makefile                   # Build targets: build, build-linux/windows/darwin, test, run
│
├── package.json               # npm package manifest (name: go-computer-use-mcp-server)
├── bin/
│   └── computer-use-mcp.js   # Node.js launcher — picks correct native binary at runtime
├── scripts/
│   └── build-npm.sh          # Cross-compiles all platforms, bundles into native/
│
├── tests/                     # Python pytest integration tests
│   ├── conftest.py            # Server subprocess fixture
│   ├── mcp_client.py          # MCP protocol client helper
│   ├── gui_helper.py          # GUI test helpers (Xvfb support)
│   ├── test_mouse.py          # Mouse tool tests
│   ├── test_keyboard.py       # Keyboard tool tests
│   ├── test_screen.py         # Screenshot / pixel color tests
│   ├── test_window_tools.py   # Window management tests
│   ├── test_process.py        # Process listing / termination tests
│   └── test_system.py         # System info tests
│
├── .github/
│   ├── workflows/             # CI/CD workflows (npm publish, etc.)
│   └── skills/                # AI agent skills (aif framework)
│       ├── go-mcp-patterns/   # Patterns for Go MCP tool development (custom)
│       ├── desktop-automation/ # robotgo automation patterns & gotchas (custom)
│       ├── aif/               # AI Factory setup skill
│       ├── aif-architecture/  # Architecture generation skill
│       ├── aif-best-practices/ # Code quality guidelines
│       ├── aif-fix/           # Bug fix workflow
│       ├── aif-plan/          # Feature planning
│       ├── aif-review/        # Code review
│       └── ...                # Other aif-* skills
│
├── .ai-factory/
│   ├── DESCRIPTION.md         # Project specification and tech stack
│   └── ARCHITECTURE.md        # Architecture decisions and patterns
├── .mcp.json                  # MCP server config for this project (GitHub MCP)
├── .ai-factory.json           # AI Factory skill registry
│
├── AGENTS.md                  # This file — project map for AI agents
├── README.md                  # User-facing documentation
├── TASKS.md                   # Implementation task list (Russian)
└── pytest.ini                 # Python test configuration
```

## Key Entry Points

| File | Purpose |
|------|---------|
| [main.go](main.go) | Entire server — all 30+ MCP tool handlers, display check, bootstrap |
| [Makefile](Makefile) | Build, test, run commands |
| [package.json](package.json) | npm distribution config |
| [bin/computer-use-mcp.js](bin/computer-use-mcp.js) | npx entry point — platform binary selector |
| [scripts/build-npm.sh](scripts/build-npm.sh) | npm release build script |
| [tests/conftest.py](tests/conftest.py) | pytest fixtures (server process lifecycle) |
| [tests/mcp_client.py](tests/mcp_client.py) | MCP JSON-RPC client for integration tests |

## MCP Tools Provided

The server exposes ~30 tools across these categories:

| Category | Tools |
|----------|-------|
| Mouse | `mouse_move`, `mouse_move_smooth`, `mouse_move_relative`, `mouse_get_position`, `mouse_click`, `mouse_click_at`, `mouse_toggle`, `mouse_drag`, `mouse_drag_smooth`, `mouse_scroll` |
| Keyboard | `keyboard_type`, `keyboard_key_tap`, `keyboard_key_toggle`, `keyboard_hotkey` |
| Screen | `screen_screenshot`, `screen_screenshot_region`, `screen_get_pixel_color`, `screen_get_size`, `screen_get_display_info` |
| Windows | `window_list`, `window_find`, `window_get_active`, `window_set_active`, `window_move`, `window_resize`, `window_minimize`, `window_maximize`, `window_close` |
| Processes | `process_list`, `process_find`, `process_get_info`, `process_terminate` |
| System | `system_info`, `system_sleep`, `xdotool_run` |

## Documentation

| Document | Path | Description |
|----------|------|-------------|
| README | [README.md](README.md) | Installation, usage, all tools reference |
| Tasks | [TASKS.md](TASKS.md) | Implementation task list (Russian) |

## AI Context Files

| File | Purpose |
|------|---------|
| [AGENTS.md](AGENTS.md) | This file — project structure map |
| [.ai-factory/DESCRIPTION.md](.ai-factory/DESCRIPTION.md) | Project specification and tech stack |
| [.ai-factory/ARCHITECTURE.md](.ai-factory/ARCHITECTURE.md) | Architecture decisions and guidelines |
| [.github/skills/go-mcp-patterns/SKILL.md](.github/skills/go-mcp-patterns/SKILL.md) | Go MCP tool development patterns |
| [.github/skills/desktop-automation/SKILL.md](.github/skills/desktop-automation/SKILL.md) | robotgo automation patterns and gotchas |

## Development Notes

- **No database** — stateless server, no persistence
- **CGO is required** — `CGO_ENABLED=0` will break the build; all CI needs GCC
- **X11 required on Linux** — set `DISPLAY` or use `Xvfb` for headless
- **Monolithic design** — all code in `main.go` by design (mirrors reference project pattern)
- **Adding a tool** — add handler func + `mcp.NewTool(...)` + `s.AddTool(...)` in `main.go`; wrap with `withDisplayCheck` if it uses robotgo; add pytest test in `tests/`