# Architecture: Layered Architecture (Monolithic main.go)

## Overview
This project follows a flat, pragmatic **Layered Architecture** within a single monolithic `main.go`. Given its nature as a system-level tool server (not a domain-rich application), there is no business domain to encapsulate — the sole responsibility is to bridge MCP protocol calls to robotgo/OS API calls. Splitting into packages would add indirection without adding clarity.

The three conceptual layers are all embedded in `main.go`:
1. **Transport Layer** — MCP protocol setup, server init, transport selection (SSE/Stdio)
2. **Handler Layer** — one function per MCP tool; validates args, calls the automation layer, returns JSON
3. **Automation Layer** — direct calls to robotgo, gosseract, gopsutil, os/exec

## Decision Rationale
- **Project type:** Infrastructure / utility server — no business domain, no persistence
- **Tech stack:** Go 1.24, mark3labs/mcp-go, robotgo (CGO), no framework
- **Team size:** 1-2 developers
- **Key factor:** The project mirrors the reference `go_mcp_server_github_api` pattern intentionally. A monolithic single-file approach maximises legibility for a tool with ~30 independent, thin handlers that each do one specific system operation.

## File Structure

```
go_computer_use_mcp_server/
│
├── main.go                 # All layers in one file (by design)
│   ├── Constants & types   # ServerName, ServerVersion, display state
│   ├── Display middleware  # checkDisplayAvailable(), withDisplayCheck()
│   ├── Argument helpers    # getIntArg, getStringArg, getRequiredXxxArg, ...
│   ├── Mouse handlers      # mouseMoveHandler, mouseClickHandler, ...
│   ├── Keyboard handlers   # keyboardTypeHandler, keyboardKeyTapHandler, ...
│   ├── Screen handlers     # screenScreenshotHandler, screenGetSizeHandler, ...
│   ├── Window handlers     # windowListHandler, windowFindHandler, ...
│   ├── Process handlers    # processListHandler, processTerminateHandler, ...
│   ├── System handlers     # systemInfoHandler, systemSleepHandler, ...
│   ├── Tool registration   # registerTools(s) — all s.AddTool() calls
│   └── main()             # Flag parsing + transport bootstrap
│
├── tests/                  # Python pytest integration tests (separate process)
│   ├── conftest.py         # Server subprocess fixture
│   ├── mcp_client.py       # MCP JSON-RPC helper
│   └── test_*.py           # One file per tool category
└── ...                     # Build, npm distribution files
```

## Dependency Rules

```
Transport Layer (server bootstrap)
    ↓
Handler Layer (per-tool functions)
    ↓
Automation Layer (robotgo / gosseract / gopsutil / os/exec)
```

- ✅ Handlers call robotgo/gopsutil/os directly
- ✅ Handlers use argument helper functions
- ✅ Tool registration calls handlers
- ✅ `main()` creates server, calls registration, starts transport
- ❌ Automation libraries do NOT know about MCP types
- ❌ No circular dependencies between handler groups
- ❌ Do NOT add shared global state beyond the display check cache

## Handler Communication

Each handler is **completely independent**:
- No shared state between handlers (except the cached display availability)
- No handler calls another handler
- No shared request/response objects

When a tool combines operations (e.g., move + click), the handler calls robotgo directly for each step — no intermediate layer.

## Key Principles

1. **One handler per tool** — each MCP tool maps to exactly one Go function. No shared "do it all" functions.
2. **Argument helpers are the only shared code** — `getIntArg`, `getStringArg`, etc. live at the top of `main.go` and are reused by all handlers.
3. **Always use `withDisplayCheck` for GUI tools** — every handler that calls robotgo must be registered via `s.AddTool(tool, withDisplayCheck(handler))`.
4. **Consistent JSON response shape** — every success response includes at minimum `{"status": "success", "message": "..."}`. Errors are returned as `nil, err`.
5. **Fail fast on missing required args** — `getRequiredXxxArg` returns an error immediately; do not fall back to zero values for required parameters.
6. **No globals that mutate during requests** — the display check uses `sync.Once` and is read-only after initialization.

## Code Examples

### Adding a new tool (complete example)

```go
// 1. Handler function
func myNewToolHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
    args := getArgs(request)

    x, err := getRequiredIntArg(args, "x")
    if err != nil {
        return nil, err
    }
    label := getStringArg(args, "label", "default")

    // Call robotgo / system API
    robotgo.Move(x, 0)

    return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
        "status":  "success",
        "message": fmt.Sprintf("Moved to x=%d with label=%s", x, label),
    })), nil
}

// 2. Tool schema
myNewTool := mcp.NewTool("my_new_tool",
    mcp.WithDescription("Short description of what this tool does"),
    mcp.WithNumber("x",
        mcp.Description("X coordinate"),
        mcp.Required(),
    ),
    mcp.WithString("label",
        mcp.Description("Optional label"),
    ),
)

// 3. Registration (inside registerTools or main)
s.AddTool(myNewTool, withDisplayCheck(myNewToolHandler))
```

### Argument extraction — required vs optional

```go
// Required — returns error if missing or wrong type
x, err := getRequiredIntArg(args, "x")
if err != nil {
    return nil, err
}

// Optional with default — never errors
timeout := getIntArg(args, "timeout", 5000)
title := getStringArg(args, "title", "")
verbose := getBoolArg(args, "verbose", false)
speed := getFloatArg(args, "speed", 1.0)
keys := getStringArrayArg(args, "keys")  // nil if missing
```

### JSON response patterns

```go
// Simple success
return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
    "status":  "success",
    "message": "Operation complete",
})), nil

// Success with data
return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
    "status": "success",
    "x":      x,
    "y":      y,
    "color":  robotgo.GetPixelColor(x, y),
})), nil

// Error (no need to wrap — mcp-go handles display)
return nil, fmt.Errorf("window %q not found", title)
```

## Anti-Patterns

- ❌ **Don't split handlers into separate files** — the monolithic `main.go` is intentional; splitting would require exporting helpers and adds friction without benefit at this scale
- ❌ **Don't call robotgo outside a `withDisplayCheck`-wrapped handler** — display check can only be bypassed intentionally (system info, process tools)
- ❌ **Don't panic on missing args** — always return `nil, err` so the MCP client gets a proper error response
- ❌ **Don't add database or file persistence** — the server is intentionally stateless
- ❌ **Don't use `CGO_ENABLED=0`** — robotgo requires CGO; pure-Go builds will fail at runtime
- ❌ **Don't share `mcp.CallToolResult` objects between handlers** — always create a fresh response
