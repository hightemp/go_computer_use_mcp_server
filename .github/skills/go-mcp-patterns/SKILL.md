---
name: go-mcp-patterns
description: Patterns and conventions for building Go MCP servers using mark3labs/mcp-go. Covers tool registration, argument extraction helpers, handler signatures, display check middleware, JSON response formatting, transport setup (SSE/Stdio), and CGO build considerations. Use when adding new MCP tools, extending an existing handler, fixing argument parsing bugs, or setting up a new Go MCP server.
argument-hint: '[topic: tools|handlers|transports|args|cgo|testing]'
allowed-tools: Read Grep Glob Write Bash(go build *) Bash(go run *) Bash(go test *) Bash(go mod *)
metadata:
  author: aif
  version: "1.0"
  category: go-development
---

# Go MCP Server Patterns (mark3labs/mcp-go)

## Project Context
This project is a monolithic Go MCP server (`main.go`) built with:
- `github.com/mark3labs/mcp-go` — MCP framework (tools, server, transports)
- `github.com/hightemp/robotgo` — desktop automation (requires CGO + X11/display)
- Transport: `stdio` (default for AI clients) and `sse` (HTTP, debugging)

---

## Tool Registration Pattern

Every tool is registered using `server.AddTool(tool, handler)`. All GUI tools are wrapped with `withDisplayCheck`.

```go
// Define the tool schema
screenshotTool := mcp.NewTool("screen_screenshot",
    mcp.WithDescription("Take a screenshot of the full screen"),
    mcp.WithNumber("display_id",
        mcp.Description("Display ID (optional, -1 for primary)"),
    ),
)

// Register with display guard
s.AddTool(screenshotTool, withDisplayCheck(screenScreenshotHandler))
```

**Non-GUI tools** (process listing, system info) skip the display guard:
```go
s.AddTool(systemInfoTool, systemInfoHandler)
```

---

## Handler Signature

All handlers follow the same signature — no exceptions:

```go
func myToolHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
    args := getArgs(request)

    // Extract parameters
    x, err := getRequiredIntArg(args, "x")
    if err != nil {
        return nil, err  // MCP client sees this as an error result
    }
    label := getStringArg(args, "label", "default value")

    // Do work ...

    // Return JSON result
    return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
        "status":  "success",
        "message": fmt.Sprintf("Done: %s at %d", label, x),
    })), nil
}
```

---

## Argument Helpers

Use these helpers (already defined in `main.go`):

| Helper | Use when |
|--------|----------|
| `getRequiredIntArg(args, "key")` | Int that must be present; returns `(int, error)` |
| `getRequiredStringArg(args, "key")` | String that must be present |
| `getIntArg(args, "key", defaultVal)` | Optional int with default |
| `getStringArg(args, "key", "default")` | Optional string with default |
| `getBoolArg(args, "key", false)` | Optional bool with default |
| `getFloatArg(args, "key", 1.0)` | Optional float64 with default |
| `getStringArrayArg(args, "key")` | Optional `[]string` |
| `getArgs(request)` | Convert raw request params to `map[string]interface{}` |

**Always call `getArgs(request)` first.** The underlying type of `request.Params.Arguments` is `interface{}` and must be type-asserted safely.

---

## Tool Schema — Common Parameter Patterns

```go
// Required integer
mcp.WithNumber("x",
    mcp.Description("X coordinate"),
    mcp.Required(),
)

// Optional string with enum values
mcp.WithString("button",
    mcp.Description("Mouse button: left, right, center"),
    mcp.DefaultValue("left"),
    mcp.Enum("left", "right", "center"),
)

// Optional bool
mcp.WithBoolean("double",
    mcp.Description("Perform double-click"),
)

// Optional string
mcp.WithString("title",
    mcp.Description("Window title substring to match"),
)
```

---

## JSON Response Format

All tools return JSON via `jsonResponse()`. Keep fields consistent:

```go
// Success response
return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
    "status":  "success",
    "message": "Human-readable description of what happened",
    // Additional result fields
    "x": x, "y": y,
})), nil

// Error — prefer returning error directly (MCP client handles formatting)
return nil, fmt.Errorf("window with title %q not found", title)

// For base64 binary data (e.g., screenshots)
return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
    "status":     "success",
    "image":      base64.StdEncoding.EncodeToString(buf.Bytes()),
    "format":     "png",
    "width":      width,
    "height":     height,
})), nil
```

---

## Display Check Middleware

The `withDisplayCheck` middleware checks `DISPLAY` env var and does a safe `robotgo.GetScreenSize()` on first call, caches the result, and returns a clear error if no display is available.

**Rules:**
- ALL `robotgo` calls MUST be wrapped with `withDisplayCheck`
- System/process tools that don't use robotgo should NOT be wrapped
- The check is lazy and cached via `sync.Once` — zero overhead after first call

```go
// withDisplayCheck signature (already in main.go)
func withDisplayCheck(handler server.ToolHandlerFunc) server.ToolHandlerFunc
```

---

## Transport Setup

```go
// main.go bootstrap pattern
func main() {
    transportType := flag.String("t", "stdio", "Transport type: stdio or sse")
    host := flag.String("h", "0.0.0.0", "SSE host")
    port := flag.Int("p", 8080, "SSE port")
    flag.Parse()

    s := server.NewMCPServer(ServerName, ServerVersion)
    registerTools(s)  // call all s.AddTool(...)

    switch *transportType {
    case "sse":
        sseServer := server.NewSSEServer(s, server.WithBaseURL(fmt.Sprintf("http://%s:%d", *host, *port)))
        log.Fatal(sseServer.Start(fmt.Sprintf("%s:%d", *host, *port)))
    default:
        if err := server.ServeStdio(s); err != nil {
            log.Fatal(err)
        }
    }
}
```

---

## CGO Constraints

This project **requires CGO**. Key implications:

- `CGO_ENABLED=0` will fail — robotgo and gosseract use C/C++ code
- Cross-compilation requires a C cross-compiler for each target:
  - Linux arm64: `aarch64-linux-gnu-gcc`
  - Windows: `x86_64-w64-mingw32-gcc`
  - macOS: requires macOS SDK (use GitHub Actions macOS runner)
- The Makefile targets (`build-linux`, `build-windows`, etc.) assume the right CC is in PATH

**Practical rule:** Build on the target OS or use CI with native runners per platform.

---

## Adding a New Tool — Checklist

1. Write the handler function: `func myNewToolHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error)`
2. Define the tool schema with `mcp.NewTool(...)`
3. Register in the `registerTools()` (or equivalent) function
4. If it uses robotgo: wrap with `withDisplayCheck`
5. Return `mcp.NewToolResultText(jsonResponse(...))` for success, `nil, err` for errors
6. Add Python pytest test in `tests/test_<category>.py`

---

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| `request.Params.Arguments` type panic | Always use `getArgs(request)` — never access directly |
| robotgo segfault without display | Always use `withDisplayCheck` middleware |
| `getRequiredIntArg` returns 0 for float inputs | The helper handles `float64` (JSON numbers) → `int` conversion automatically |
| CGO cross-compile fails | Each OS needs its own runner/toolchain — don't try `GOOS=darwin` on Linux without the SDK |
| MCP tool not appearing | Check that `s.AddTool` is called before `ServeStdio` or `sseServer.Start` |
