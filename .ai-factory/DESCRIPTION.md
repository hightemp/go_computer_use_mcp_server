# Project: go_computer_use_mcp_server

## Overview
MCP (Model Context Protocol) server written in Go for desktop computer automation. Exposes rich computer-use capabilities — mouse, keyboard, screen, window management, process control, OCR, and system utilities — over both SSE and Stdio transports. Packaged and distributed as an npm wrapper so AI agents can install it with a single `npx` command without requiring a Go toolchain.

## Core Features
- **Mouse control**: move, smooth move, relative move, click, double-click, drag, smooth drag, scroll, toggle
- **Keyboard control**: key presses, simultaneous key input, text typing, hotkeys/shortcuts, special keys
- **Screen operations**: full-screen and region screenshots (base64 PNG), pixel color query, display size/info, multi-monitor support
- **Window management**: list windows, find by title, move, resize, minimize, maximize, close, focus, get active window
- **Process management**: list all processes, search by name/PID, get details, terminate
- **System utilities**: system info (CPU, RAM, OS, architecture), `xdotool` command passthrough, configurable delays
- **OCR** (via `gosseract`): extract text from screen regions
- **Display check**: graceful no-display error when `DISPLAY` is not set (X11/Linux)

## Tech Stack
- **Language:** Go 1.24
- **MCP Framework:** `github.com/mark3labs/mcp-go` (v0.31+)
- **Desktop Automation:** `github.com/hightemp/robotgo` (fork of robotgo — custom `robotgo` with extra APIs)
- **OCR:** `github.com/otiai10/gosseract/v2`
- **System Info:** `github.com/shirou/gopsutil/v4`
- **Transport:** SSE (HTTP) + Stdio
- **Distribution (npm):** Node.js wrapper script in `bin/` + `package.json`; binary bundled under `native/`
- **Tests:** Python + pytest integration suite (tests via subprocess MCP client)

## Architecture Notes
- **Monolithic main.go** (~1500 lines): all tool handlers, registration, argument helpers, and server bootstrap in one file. Pattern mirrors `go_mcp_server_github_api` reference project.
- **Handler registration pattern**: every tool is registered with `server.AddTool(mcpTool, withDisplayCheck(handler))`. The `withDisplayCheck` middleware guards every GUI-requiring tool.
- **Transport selection**: CLI flags `-t stdio|sse`, `-h host`, `-p port`.
- **Cross-platform build targets**: Linux (amd64/arm64), Windows (amd64), macOS (amd64/arm64) via `Makefile`.
- **npm distribution**: `scripts/build-npm.sh` cross-compiles and bundles into `native/`; `bin/computer-use-mcp.js` picks the right binary at runtime.

## Non-Functional Requirements
- **Display safety**: all GUI tools wrapped in `withDisplayCheck` — returns a clear error if no X11 display instead of crashing
- **Error handling**: structured JSON responses with `status` + `message` fields; tool handler errors bubble up as MCP error results
- **Logging:** stderr via `log` package
- **JSON responses:** all `mcp.NewToolResultText(jsonResponse(...))` — consistent JSON in content
- **CGO**: required (robotgo + gosseract use CGO); pure-Go cross-compilation is NOT possible for this project

## Architecture
See `.ai-factory/ARCHITECTURE.md` for detailed architecture guidelines.
Pattern: Layered Architecture (Monolithic main.go)
