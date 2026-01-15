package main

import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"flag"
	"fmt"
	"image/png"
	"log"

	"github.com/hightemp/robotgo"
	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
)

const (
	ServerName    = "go_computer_use_mcp_server"
	ServerVersion = "1.0.0"
)

// Helper function to create JSON response
func jsonResponse(data interface{}) string {
	jsonBytes, err := json.MarshalIndent(data, "", "  ")
	if err != nil {
		return fmt.Sprintf(`{"error": "%s"}`, err.Error())
	}
	return string(jsonBytes)
}

// Helper function to get int argument
func getIntArg(args map[string]interface{}, key string, defaultVal int) int {
	if val, ok := args[key]; ok {
		switch v := val.(type) {
		case float64:
			return int(v)
		case int:
			return v
		case int64:
			return int(v)
		}
	}
	return defaultVal
}

// Helper function to get required int argument
func getRequiredIntArg(args map[string]interface{}, key string) (int, error) {
	if val, ok := args[key]; ok {
		switch v := val.(type) {
		case float64:
			return int(v), nil
		case int:
			return v, nil
		case int64:
			return int(v), nil
		}
	}
	return 0, fmt.Errorf("required parameter '%s' is missing", key)
}

// Helper function to get string argument
func getStringArg(args map[string]interface{}, key string, defaultVal string) string {
	if val, ok := args[key]; ok {
		if s, ok := val.(string); ok {
			return s
		}
	}
	return defaultVal
}

// Helper function to get required string argument
func getRequiredStringArg(args map[string]interface{}, key string) (string, error) {
	if val, ok := args[key]; ok {
		if s, ok := val.(string); ok {
			return s, nil
		}
	}
	return "", fmt.Errorf("required parameter '%s' is missing", key)
}

// Helper function to get bool argument
func getBoolArg(args map[string]interface{}, key string, defaultVal bool) bool {
	if val, ok := args[key]; ok {
		if b, ok := val.(bool); ok {
			return b
		}
	}
	return defaultVal
}

// Helper function to get float argument
func getFloatArg(args map[string]interface{}, key string, defaultVal float64) float64 {
	if val, ok := args[key]; ok {
		switch v := val.(type) {
		case float64:
			return v
		case int:
			return float64(v)
		case int64:
			return float64(v)
		}
	}
	return defaultVal
}

// Helper function to get string array argument
func getStringArrayArg(args map[string]interface{}, key string) []string {
	if val, ok := args[key]; ok {
		if arr, ok := val.([]interface{}); ok {
			result := make([]string, 0, len(arr))
			for _, item := range arr {
				if s, ok := item.(string); ok {
					result = append(result, s)
				}
			}
			return result
		}
	}
	return nil
}

// Helper function to get args as map
func getArgs(request mcp.CallToolRequest) map[string]interface{} {
	if args, ok := request.Params.Arguments.(map[string]interface{}); ok {
		return args
	}
	return make(map[string]interface{})
}

// ==================== MOUSE HANDLERS ====================

func mouseMoveHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	x, err := getRequiredIntArg(args, "x")
	if err != nil {
		return nil, err
	}
	y, err := getRequiredIntArg(args, "y")
	if err != nil {
		return nil, err
	}

	displayId := getIntArg(args, "display_id", -1)

	if displayId >= 0 {
		robotgo.Move(x, y, displayId)
	} else {
		robotgo.Move(x, y)
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": fmt.Sprintf("Mouse moved to (%d, %d)", x, y),
	})), nil
}

func mouseMoveSmoothHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	x, err := getRequiredIntArg(args, "x")
	if err != nil {
		return nil, err
	}
	y, err := getRequiredIntArg(args, "y")
	if err != nil {
		return nil, err
	}

	low := getFloatArg(args, "low", 1.0)
	high := getFloatArg(args, "high", 3.0)

	success := robotgo.MoveSmooth(x, y, low, high)

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"success": success,
		"message": fmt.Sprintf("Mouse moved smoothly to (%d, %d)", x, y),
	})), nil
}

func mouseMoveRelativeHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	x, err := getRequiredIntArg(args, "x")
	if err != nil {
		return nil, err
	}
	y, err := getRequiredIntArg(args, "y")
	if err != nil {
		return nil, err
	}

	robotgo.MoveRelative(x, y)

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": fmt.Sprintf("Mouse moved relative by (%d, %d)", x, y),
	})), nil
}

func mouseGetPositionHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	x, y := robotgo.Location()

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"x": x,
		"y": y,
	})), nil
}

func mouseClickHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	button := getStringArg(args, "button", "left")
	double := getBoolArg(args, "double", false)

	if double {
		robotgo.Click(button, true)
	} else {
		robotgo.Click(button)
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": fmt.Sprintf("Mouse %s click performed", button),
	})), nil
}

func mouseClickAtHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	x, err := getRequiredIntArg(args, "x")
	if err != nil {
		return nil, err
	}
	y, err := getRequiredIntArg(args, "y")
	if err != nil {
		return nil, err
	}

	button := getStringArg(args, "button", "left")
	double := getBoolArg(args, "double", false)

	if double {
		robotgo.MoveClick(x, y, button, true)
	} else {
		robotgo.MoveClick(x, y, button)
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": fmt.Sprintf("Mouse %s click at (%d, %d)", button, x, y),
	})), nil
}

func mouseToggleHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	button := getStringArg(args, "button", "left")
	down := getBoolArg(args, "down", true)

	var action string
	if down {
		action = "down"
		robotgo.Toggle(button, "down")
	} else {
		action = "up"
		robotgo.Toggle(button, "up")
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": fmt.Sprintf("Mouse button %s %s", button, action),
	})), nil
}

func mouseDragHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	x, err := getRequiredIntArg(args, "x")
	if err != nil {
		return nil, err
	}
	y, err := getRequiredIntArg(args, "y")
	if err != nil {
		return nil, err
	}

	button := getStringArg(args, "button", "left")

	robotgo.Drag(x, y, button)

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": fmt.Sprintf("Mouse dragged to (%d, %d)", x, y),
	})), nil
}

func mouseDragSmoothHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	x, err := getRequiredIntArg(args, "x")
	if err != nil {
		return nil, err
	}
	y, err := getRequiredIntArg(args, "y")
	if err != nil {
		return nil, err
	}

	low := getFloatArg(args, "low", 1.0)
	high := getFloatArg(args, "high", 3.0)
	button := getStringArg(args, "button", "left")

	robotgo.DragSmooth(x, y, low, high, button)

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": fmt.Sprintf("Mouse dragged smoothly to (%d, %d)", x, y),
	})), nil
}

func mouseScrollHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	x, err := getRequiredIntArg(args, "x")
	if err != nil {
		return nil, err
	}
	y, err := getRequiredIntArg(args, "y")
	if err != nil {
		return nil, err
	}

	displayId := getIntArg(args, "display_id", -1)

	if displayId >= 0 {
		robotgo.Scroll(x, y, displayId)
	} else {
		robotgo.Scroll(x, y)
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": fmt.Sprintf("Mouse scrolled (%d, %d)", x, y),
	})), nil
}

func mouseScrollDirectionHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	amount, err := getRequiredIntArg(args, "amount")
	if err != nil {
		return nil, err
	}

	direction, err := getRequiredStringArg(args, "direction")
	if err != nil {
		return nil, err
	}

	robotgo.ScrollDir(amount, direction)

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": fmt.Sprintf("Mouse scrolled %s by %d", direction, amount),
	})), nil
}

func mouseScrollSmoothHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	to, err := getRequiredIntArg(args, "to")
	if err != nil {
		return nil, err
	}

	num := getIntArg(args, "num", 5)
	delay := getIntArg(args, "delay", 100)

	robotgo.ScrollSmooth(to, num, delay)

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": fmt.Sprintf("Mouse scrolled smoothly to %d", to),
	})), nil
}

// ==================== KEYBOARD HANDLERS ====================

func keyTapHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	key, err := getRequiredStringArg(args, "key")
	if err != nil {
		return nil, err
	}

	modifiers := getStringArrayArg(args, "modifiers")

	if len(modifiers) > 0 {
		modifierInterfaces := make([]interface{}, len(modifiers))
		for i, m := range modifiers {
			modifierInterfaces[i] = m
		}
		robotgo.KeyTap(key, modifierInterfaces...)
	} else {
		robotgo.KeyTap(key)
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": fmt.Sprintf("Key '%s' tapped", key),
	})), nil
}

func keyToggleHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	key, err := getRequiredStringArg(args, "key")
	if err != nil {
		return nil, err
	}

	down := getBoolArg(args, "down", true)

	var action string
	if down {
		action = "down"
		robotgo.KeyToggle(key, "down")
	} else {
		action = "up"
		robotgo.KeyToggle(key, "up")
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": fmt.Sprintf("Key '%s' %s", key, action),
	})), nil
}

func typeTextHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	text, err := getRequiredStringArg(args, "text")
	if err != nil {
		return nil, err
	}

	delay := getIntArg(args, "delay", 0)

	if delay > 0 {
		robotgo.TypeDelay(text, delay)
	} else {
		robotgo.Type(text)
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": fmt.Sprintf("Text typed: %d characters", len(text)),
	})), nil
}

func typeTextDelayedHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	text, err := getRequiredStringArg(args, "text")
	if err != nil {
		return nil, err
	}

	delay, err := getRequiredIntArg(args, "delay")
	if err != nil {
		return nil, err
	}

	robotgo.TypeDelay(text, delay)

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": fmt.Sprintf("Text typed with %dms delay: %d characters", delay, len(text)),
	})), nil
}

func clipboardReadHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	text, err := robotgo.ReadAll()
	if err != nil {
		return nil, fmt.Errorf("failed to read clipboard: %w", err)
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"text": text,
	})), nil
}

func clipboardWriteHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	text, err := getRequiredStringArg(args, "text")
	if err != nil {
		return nil, err
	}

	err = robotgo.WriteAll(text)
	if err != nil {
		return nil, fmt.Errorf("failed to write to clipboard: %w", err)
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": "Text written to clipboard",
	})), nil
}

func clipboardPasteHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	text, err := getRequiredStringArg(args, "text")
	if err != nil {
		return nil, err
	}

	err = robotgo.Paste(text)
	if err != nil {
		return nil, fmt.Errorf("failed to paste text: %w", err)
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": "Text pasted via clipboard",
	})), nil
}

// ==================== SCREEN HANDLERS ====================

func screenGetSizeHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	displayId := getIntArg(args, "display_id", -1)

	var width, height int
	if displayId >= 0 {
		width, height = robotgo.GetScaleSize(displayId)
	} else {
		width, height = robotgo.GetScreenSize()
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"width":  width,
		"height": height,
	})), nil
}

func screenGetDisplaysNumHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	count := robotgo.DisplaysNum()

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"count": count,
	})), nil
}

func screenGetDisplayBoundsHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	displayId, err := getRequiredIntArg(args, "display_id")
	if err != nil {
		return nil, err
	}

	x, y, w, h := robotgo.GetDisplayBounds(displayId)

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"x":      x,
		"y":      y,
		"width":  w,
		"height": h,
	})), nil
}

func screenCaptureHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	x := getIntArg(args, "x", -1)
	y := getIntArg(args, "y", -1)
	width := getIntArg(args, "width", -1)
	height := getIntArg(args, "height", -1)
	displayId := getIntArg(args, "display_id", -1)

	var img *robotgo.CBitmap
	var captureArgs []int

	if x >= 0 && y >= 0 && width > 0 && height > 0 {
		captureArgs = append(captureArgs, x, y, width, height)
	}
	if displayId >= 0 {
		if len(captureArgs) == 0 {
			// Need to capture full screen first
			sw, sh := robotgo.GetScreenSize()
			captureArgs = append(captureArgs, 0, 0, sw, sh)
		}
		captureArgs = append(captureArgs, displayId)
	}

	var bitmap robotgo.CBitmap
	if len(captureArgs) > 0 {
		bitmap = robotgo.CaptureScreen(captureArgs...)
	} else {
		bitmap = robotgo.CaptureScreen()
	}
	img = &bitmap
	defer robotgo.FreeBitmap(*img)

	// Convert to image
	image := robotgo.ToImage(*img)

	// Encode to PNG
	var buf bytes.Buffer
	err := png.Encode(&buf, image)
	if err != nil {
		return nil, fmt.Errorf("failed to encode image: %w", err)
	}

	// Base64 encode
	base64Str := base64.StdEncoding.EncodeToString(buf.Bytes())

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"image":    base64Str,
		"format":   "png",
		"encoding": "base64",
	})), nil
}

func screenCaptureSaveHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	path, err := getRequiredStringArg(args, "path")
	if err != nil {
		return nil, err
	}

	x := getIntArg(args, "x", -1)
	y := getIntArg(args, "y", -1)
	width := getIntArg(args, "width", -1)
	height := getIntArg(args, "height", -1)

	var captureArgs []int
	if x >= 0 && y >= 0 && width > 0 && height > 0 {
		captureArgs = append(captureArgs, x, y, width, height)
	}

	err = robotgo.SaveCapture(path, captureArgs...)
	if err != nil {
		return nil, fmt.Errorf("failed to save capture: %w", err)
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": fmt.Sprintf("Screenshot saved to %s", path),
		"path":    path,
	})), nil
}

func screenGetPixelColorHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	x, err := getRequiredIntArg(args, "x")
	if err != nil {
		return nil, err
	}
	y, err := getRequiredIntArg(args, "y")
	if err != nil {
		return nil, err
	}

	displayId := getIntArg(args, "display_id", -1)

	var color string
	if displayId >= 0 {
		color = robotgo.GetPixelColor(x, y, displayId)
	} else {
		color = robotgo.GetPixelColor(x, y)
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"color": color,
	})), nil
}

func screenGetMouseColorHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	displayId := getIntArg(args, "display_id", -1)

	var color string
	if displayId >= 0 {
		color = robotgo.GetLocationColor(displayId)
	} else {
		color = robotgo.GetLocationColor()
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"color": color,
	})), nil
}

// ==================== WINDOW HANDLERS ====================

func windowGetActiveHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	handle := robotgo.GetActive()
	title := robotgo.GetTitle()
	pid := robotgo.GetPid()

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"handle": handle,
		"title":  title,
		"pid":    pid,
	})), nil
}

func windowGetTitleHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	pid := getIntArg(args, "pid", -1)

	var title string
	if pid >= 0 {
		title = robotgo.GetTitle(pid)
	} else {
		title = robotgo.GetTitle()
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"title": title,
	})), nil
}

func windowGetBoundsHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	pid, err := getRequiredIntArg(args, "pid")
	if err != nil {
		return nil, err
	}

	x, y, w, h := robotgo.GetBounds(pid)

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"x":      x,
		"y":      y,
		"width":  w,
		"height": h,
	})), nil
}

func windowSetActiveHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	pid, err := getRequiredIntArg(args, "pid")
	if err != nil {
		return nil, err
	}

	err = robotgo.ActivePid(pid)
	if err != nil {
		return nil, fmt.Errorf("failed to activate window: %w", err)
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": fmt.Sprintf("Window with PID %d activated", pid),
	})), nil
}

func windowMoveHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	pid, err := getRequiredIntArg(args, "pid")
	if err != nil {
		return nil, err
	}
	x, err := getRequiredIntArg(args, "x")
	if err != nil {
		return nil, err
	}
	y, err := getRequiredIntArg(args, "y")
	if err != nil {
		return nil, err
	}

	robotgo.MoveWindow(pid, x, y)

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": fmt.Sprintf("Window moved to (%d, %d)", x, y),
	})), nil
}

func windowResizeHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	pid, err := getRequiredIntArg(args, "pid")
	if err != nil {
		return nil, err
	}
	width, err := getRequiredIntArg(args, "width")
	if err != nil {
		return nil, err
	}
	height, err := getRequiredIntArg(args, "height")
	if err != nil {
		return nil, err
	}

	robotgo.ResizeWindow(pid, width, height)

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": fmt.Sprintf("Window resized to %dx%d", width, height),
	})), nil
}

func windowMinimizeHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	pid, err := getRequiredIntArg(args, "pid")
	if err != nil {
		return nil, err
	}

	robotgo.MinWindow(pid)

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": "Window minimized",
	})), nil
}

func windowMaximizeHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	pid, err := getRequiredIntArg(args, "pid")
	if err != nil {
		return nil, err
	}

	robotgo.MaxWindow(pid)

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": "Window maximized",
	})), nil
}

func windowCloseHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	pid := getIntArg(args, "pid", -1)

	if pid >= 0 {
		robotgo.CloseWindow(pid)
	} else {
		robotgo.CloseWindow()
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": "Window closed",
	})), nil
}

// ==================== PROCESS HANDLERS ====================

func processListHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	processes, err := robotgo.Process()
	if err != nil {
		return nil, fmt.Errorf("failed to get process list: %w", err)
	}

	processList := make([]map[string]interface{}, 0, len(processes))
	for _, p := range processes {
		processList = append(processList, map[string]interface{}{
			"pid":  p.Pid,
			"name": p.Name,
		})
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"processes": processList,
		"count":     len(processList),
	})), nil
}

func processFindByNameHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	name, err := getRequiredStringArg(args, "name")
	if err != nil {
		return nil, err
	}

	pids, err := robotgo.FindIds(name)
	if err != nil {
		return nil, fmt.Errorf("failed to find processes: %w", err)
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"pids":  pids,
		"count": len(pids),
	})), nil
}

func processGetNameHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	pid, err := getRequiredIntArg(args, "pid")
	if err != nil {
		return nil, err
	}

	name, err := robotgo.FindName(pid)
	if err != nil {
		return nil, fmt.Errorf("failed to get process name: %w", err)
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"name": name,
	})), nil
}

func processExistsHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	pid, err := getRequiredIntArg(args, "pid")
	if err != nil {
		return nil, err
	}

	exists, err := robotgo.PidExists(pid)
	if err != nil {
		return nil, fmt.Errorf("failed to check process: %w", err)
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"exists": exists,
	})), nil
}

func processKillHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	pid, err := getRequiredIntArg(args, "pid")
	if err != nil {
		return nil, err
	}

	err = robotgo.Kill(pid)
	if err != nil {
		return nil, fmt.Errorf("failed to kill process: %w", err)
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": fmt.Sprintf("Process %d killed", pid),
	})), nil
}

func processRunHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	command, err := getRequiredStringArg(args, "command")
	if err != nil {
		return nil, err
	}

	output, err := robotgo.Run(command)
	if err != nil {
		return nil, fmt.Errorf("failed to run command: %w", err)
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"output": string(output),
	})), nil
}

// ==================== SYSTEM HANDLERS ====================

func systemGetInfoHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	version := robotgo.GetVersion()
	is64Bit := robotgo.Is64Bit()
	mainDisplayId := robotgo.GetMainId()
	displaysCount := robotgo.DisplaysNum()

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"version":         version,
		"is_64bit":        is64Bit,
		"main_display_id": mainDisplayId,
		"displays_count":  displaysCount,
	})), nil
}

func utilSleepHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	milliseconds, err := getRequiredIntArg(args, "milliseconds")
	if err != nil {
		return nil, err
	}

	robotgo.MilliSleep(milliseconds)

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"status":  "success",
		"message": fmt.Sprintf("Slept for %d milliseconds", milliseconds),
	})), nil
}

func alertShowHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := getArgs(request)

	title, err := getRequiredStringArg(args, "title")
	if err != nil {
		return nil, err
	}
	message, err := getRequiredStringArg(args, "message")
	if err != nil {
		return nil, err
	}

	defaultBtn := getStringArg(args, "default_btn", "OK")
	cancelBtn := getStringArg(args, "cancel_btn", "")

	var clickedDefault bool
	if cancelBtn != "" {
		clickedDefault = robotgo.Alert(title, message, defaultBtn, cancelBtn)
	} else {
		clickedDefault = robotgo.Alert(title, message, defaultBtn)
	}

	return mcp.NewToolResultText(jsonResponse(map[string]interface{}{
		"clicked_default": clickedDefault,
	})), nil
}

// ==================== TOOL REGISTRATION ====================

func registerMouseTools(mcpServer *server.MCPServer) {
	// mouse_move
	mcpServer.AddTool(mcp.NewTool("mouse_move",
		mcp.WithDescription("Move mouse cursor to absolute position (x, y)"),
		mcp.WithNumber("x", mcp.Required(), mcp.Description("X coordinate")),
		mcp.WithNumber("y", mcp.Required(), mcp.Description("Y coordinate")),
		mcp.WithNumber("display_id", mcp.Description("Display ID (optional)")),
	), mouseMoveHandler)

	// mouse_move_smooth
	mcpServer.AddTool(mcp.NewTool("mouse_move_smooth",
		mcp.WithDescription("Move mouse cursor smoothly (human-like) to position"),
		mcp.WithNumber("x", mcp.Required(), mcp.Description("X coordinate")),
		mcp.WithNumber("y", mcp.Required(), mcp.Description("Y coordinate")),
		mcp.WithNumber("low", mcp.Description("Low speed factor (default: 1.0)")),
		mcp.WithNumber("high", mcp.Description("High speed factor (default: 3.0)")),
	), mouseMoveSmoothHandler)

	// mouse_move_relative
	mcpServer.AddTool(mcp.NewTool("mouse_move_relative",
		mcp.WithDescription("Move mouse cursor relative to current position"),
		mcp.WithNumber("x", mcp.Required(), mcp.Description("X offset")),
		mcp.WithNumber("y", mcp.Required(), mcp.Description("Y offset")),
	), mouseMoveRelativeHandler)

	// mouse_get_position
	mcpServer.AddTool(mcp.NewTool("mouse_get_position",
		mcp.WithDescription("Get current mouse cursor position"),
	), mouseGetPositionHandler)

	// mouse_click
	mcpServer.AddTool(mcp.NewTool("mouse_click",
		mcp.WithDescription("Perform mouse click"),
		mcp.WithString("button", mcp.Description("Button: 'left', 'right', 'center' (default: 'left')")),
		mcp.WithBoolean("double", mcp.Description("Double click (default: false)")),
	), mouseClickHandler)

	// mouse_click_at
	mcpServer.AddTool(mcp.NewTool("mouse_click_at",
		mcp.WithDescription("Move mouse to position and click"),
		mcp.WithNumber("x", mcp.Required(), mcp.Description("X coordinate")),
		mcp.WithNumber("y", mcp.Required(), mcp.Description("Y coordinate")),
		mcp.WithString("button", mcp.Description("Button: 'left', 'right', 'center' (default: 'left')")),
		mcp.WithBoolean("double", mcp.Description("Double click (default: false)")),
	), mouseClickAtHandler)

	// mouse_toggle
	mcpServer.AddTool(mcp.NewTool("mouse_toggle",
		mcp.WithDescription("Press or release mouse button"),
		mcp.WithString("button", mcp.Description("Button: 'left', 'right', 'center' (default: 'left')")),
		mcp.WithBoolean("down", mcp.Description("true to press down, false to release (default: true)")),
	), mouseToggleHandler)

	// mouse_drag
	mcpServer.AddTool(mcp.NewTool("mouse_drag",
		mcp.WithDescription("Drag mouse to position"),
		mcp.WithNumber("x", mcp.Required(), mcp.Description("X coordinate")),
		mcp.WithNumber("y", mcp.Required(), mcp.Description("Y coordinate")),
		mcp.WithString("button", mcp.Description("Button to hold during drag (default: 'left')")),
	), mouseDragHandler)

	// mouse_drag_smooth
	mcpServer.AddTool(mcp.NewTool("mouse_drag_smooth",
		mcp.WithDescription("Drag mouse smoothly to position"),
		mcp.WithNumber("x", mcp.Required(), mcp.Description("X coordinate")),
		mcp.WithNumber("y", mcp.Required(), mcp.Description("Y coordinate")),
		mcp.WithNumber("low", mcp.Description("Low speed factor (default: 1.0)")),
		mcp.WithNumber("high", mcp.Description("High speed factor (default: 3.0)")),
		mcp.WithString("button", mcp.Description("Button to hold during drag (default: 'left')")),
	), mouseDragSmoothHandler)

	// mouse_scroll
	mcpServer.AddTool(mcp.NewTool("mouse_scroll",
		mcp.WithDescription("Scroll mouse wheel"),
		mcp.WithNumber("x", mcp.Required(), mcp.Description("Horizontal scroll amount")),
		mcp.WithNumber("y", mcp.Required(), mcp.Description("Vertical scroll amount")),
		mcp.WithNumber("display_id", mcp.Description("Display ID (optional)")),
	), mouseScrollHandler)

	// mouse_scroll_direction
	mcpServer.AddTool(mcp.NewTool("mouse_scroll_direction",
		mcp.WithDescription("Scroll in a specific direction"),
		mcp.WithNumber("amount", mcp.Required(), mcp.Description("Scroll amount")),
		mcp.WithString("direction", mcp.Required(), mcp.Description("Direction: 'up', 'down', 'left', 'right'")),
	), mouseScrollDirectionHandler)

	// mouse_scroll_smooth
	mcpServer.AddTool(mcp.NewTool("mouse_scroll_smooth",
		mcp.WithDescription("Scroll smoothly"),
		mcp.WithNumber("to", mcp.Required(), mcp.Description("Target scroll position")),
		mcp.WithNumber("num", mcp.Description("Number of scroll steps (default: 5)")),
		mcp.WithNumber("delay", mcp.Description("Delay between steps in ms (default: 100)")),
	), mouseScrollSmoothHandler)
}

func registerKeyboardTools(mcpServer *server.MCPServer) {
	// key_tap
	mcpServer.AddTool(mcp.NewTool("key_tap",
		mcp.WithDescription("Tap a key (press and release)"),
		mcp.WithString("key", mcp.Required(), mcp.Description("Key to tap (e.g., 'a', 'enter', 'f1')")),
		mcp.WithArray("modifiers", mcp.Description("Modifier keys: 'alt', 'ctrl', 'shift', 'cmd'")),
	), keyTapHandler)

	// key_toggle
	mcpServer.AddTool(mcp.NewTool("key_toggle",
		mcp.WithDescription("Press or release a key"),
		mcp.WithString("key", mcp.Required(), mcp.Description("Key to toggle")),
		mcp.WithBoolean("down", mcp.Description("true to press down, false to release (default: true)")),
	), keyToggleHandler)

	// type_text
	mcpServer.AddTool(mcp.NewTool("type_text",
		mcp.WithDescription("Type text (supports UTF-8)"),
		mcp.WithString("text", mcp.Required(), mcp.Description("Text to type")),
		mcp.WithNumber("delay", mcp.Description("Delay between characters in ms (optional)")),
	), typeTextHandler)

	// type_text_delayed
	mcpServer.AddTool(mcp.NewTool("type_text_delayed",
		mcp.WithDescription("Type text with a specific delay between characters"),
		mcp.WithString("text", mcp.Required(), mcp.Description("Text to type")),
		mcp.WithNumber("delay", mcp.Required(), mcp.Description("Delay between characters in ms")),
	), typeTextDelayedHandler)

	// clipboard_read
	mcpServer.AddTool(mcp.NewTool("clipboard_read",
		mcp.WithDescription("Read text from clipboard"),
	), clipboardReadHandler)

	// clipboard_write
	mcpServer.AddTool(mcp.NewTool("clipboard_write",
		mcp.WithDescription("Write text to clipboard"),
		mcp.WithString("text", mcp.Required(), mcp.Description("Text to write to clipboard")),
	), clipboardWriteHandler)

	// clipboard_paste
	mcpServer.AddTool(mcp.NewTool("clipboard_paste",
		mcp.WithDescription("Paste text via clipboard (writes to clipboard and simulates Ctrl+V/Cmd+V)"),
		mcp.WithString("text", mcp.Required(), mcp.Description("Text to paste")),
	), clipboardPasteHandler)
}

func registerScreenTools(mcpServer *server.MCPServer) {
	// screen_get_size
	mcpServer.AddTool(mcp.NewTool("screen_get_size",
		mcp.WithDescription("Get screen size"),
		mcp.WithNumber("display_id", mcp.Description("Display ID (optional)")),
	), screenGetSizeHandler)

	// screen_get_displays_num
	mcpServer.AddTool(mcp.NewTool("screen_get_displays_num",
		mcp.WithDescription("Get number of displays/monitors"),
	), screenGetDisplaysNumHandler)

	// screen_get_display_bounds
	mcpServer.AddTool(mcp.NewTool("screen_get_display_bounds",
		mcp.WithDescription("Get display bounds (x, y, width, height)"),
		mcp.WithNumber("display_id", mcp.Required(), mcp.Description("Display ID")),
	), screenGetDisplayBoundsHandler)

	// screen_capture
	mcpServer.AddTool(mcp.NewTool("screen_capture",
		mcp.WithDescription("Capture screenshot (returns base64 PNG)"),
		mcp.WithNumber("x", mcp.Description("X coordinate (optional)")),
		mcp.WithNumber("y", mcp.Description("Y coordinate (optional)")),
		mcp.WithNumber("width", mcp.Description("Width (optional)")),
		mcp.WithNumber("height", mcp.Description("Height (optional)")),
		mcp.WithNumber("display_id", mcp.Description("Display ID (optional)")),
	), screenCaptureHandler)

	// screen_capture_save
	mcpServer.AddTool(mcp.NewTool("screen_capture_save",
		mcp.WithDescription("Capture screenshot and save to file"),
		mcp.WithString("path", mcp.Required(), mcp.Description("File path to save screenshot")),
		mcp.WithNumber("x", mcp.Description("X coordinate (optional)")),
		mcp.WithNumber("y", mcp.Description("Y coordinate (optional)")),
		mcp.WithNumber("width", mcp.Description("Width (optional)")),
		mcp.WithNumber("height", mcp.Description("Height (optional)")),
	), screenCaptureSaveHandler)

	// screen_get_pixel_color
	mcpServer.AddTool(mcp.NewTool("screen_get_pixel_color",
		mcp.WithDescription("Get pixel color at position"),
		mcp.WithNumber("x", mcp.Required(), mcp.Description("X coordinate")),
		mcp.WithNumber("y", mcp.Required(), mcp.Description("Y coordinate")),
		mcp.WithNumber("display_id", mcp.Description("Display ID (optional)")),
	), screenGetPixelColorHandler)

	// screen_get_mouse_color
	mcpServer.AddTool(mcp.NewTool("screen_get_mouse_color",
		mcp.WithDescription("Get pixel color at current mouse position"),
		mcp.WithNumber("display_id", mcp.Description("Display ID (optional)")),
	), screenGetMouseColorHandler)
}

func registerWindowTools(mcpServer *server.MCPServer) {
	// window_get_active
	mcpServer.AddTool(mcp.NewTool("window_get_active",
		mcp.WithDescription("Get active window information"),
	), windowGetActiveHandler)

	// window_get_title
	mcpServer.AddTool(mcp.NewTool("window_get_title",
		mcp.WithDescription("Get window title"),
		mcp.WithNumber("pid", mcp.Description("Process ID (optional, uses active window if not specified)")),
	), windowGetTitleHandler)

	// window_get_bounds
	mcpServer.AddTool(mcp.NewTool("window_get_bounds",
		mcp.WithDescription("Get window bounds (x, y, width, height)"),
		mcp.WithNumber("pid", mcp.Required(), mcp.Description("Process ID")),
	), windowGetBoundsHandler)

	// window_set_active
	mcpServer.AddTool(mcp.NewTool("window_set_active",
		mcp.WithDescription("Activate window by PID"),
		mcp.WithNumber("pid", mcp.Required(), mcp.Description("Process ID")),
	), windowSetActiveHandler)

	// window_move
	mcpServer.AddTool(mcp.NewTool("window_move",
		mcp.WithDescription("Move window to position"),
		mcp.WithNumber("pid", mcp.Required(), mcp.Description("Process ID")),
		mcp.WithNumber("x", mcp.Required(), mcp.Description("X coordinate")),
		mcp.WithNumber("y", mcp.Required(), mcp.Description("Y coordinate")),
	), windowMoveHandler)

	// window_resize
	mcpServer.AddTool(mcp.NewTool("window_resize",
		mcp.WithDescription("Resize window"),
		mcp.WithNumber("pid", mcp.Required(), mcp.Description("Process ID")),
		mcp.WithNumber("width", mcp.Required(), mcp.Description("New width")),
		mcp.WithNumber("height", mcp.Required(), mcp.Description("New height")),
	), windowResizeHandler)

	// window_minimize
	mcpServer.AddTool(mcp.NewTool("window_minimize",
		mcp.WithDescription("Minimize window"),
		mcp.WithNumber("pid", mcp.Required(), mcp.Description("Process ID")),
	), windowMinimizeHandler)

	// window_maximize
	mcpServer.AddTool(mcp.NewTool("window_maximize",
		mcp.WithDescription("Maximize window"),
		mcp.WithNumber("pid", mcp.Required(), mcp.Description("Process ID")),
	), windowMaximizeHandler)

	// window_close
	mcpServer.AddTool(mcp.NewTool("window_close",
		mcp.WithDescription("Close window"),
		mcp.WithNumber("pid", mcp.Description("Process ID (optional, closes active window if not specified)")),
	), windowCloseHandler)
}

func registerProcessTools(mcpServer *server.MCPServer) {
	// process_list
	mcpServer.AddTool(mcp.NewTool("process_list",
		mcp.WithDescription("List all running processes"),
	), processListHandler)

	// process_find_by_name
	mcpServer.AddTool(mcp.NewTool("process_find_by_name",
		mcp.WithDescription("Find processes by name (case insensitive)"),
		mcp.WithString("name", mcp.Required(), mcp.Description("Process name to search for")),
	), processFindByNameHandler)

	// process_get_name
	mcpServer.AddTool(mcp.NewTool("process_get_name",
		mcp.WithDescription("Get process name by PID"),
		mcp.WithNumber("pid", mcp.Required(), mcp.Description("Process ID")),
	), processGetNameHandler)

	// process_exists
	mcpServer.AddTool(mcp.NewTool("process_exists",
		mcp.WithDescription("Check if process exists"),
		mcp.WithNumber("pid", mcp.Required(), mcp.Description("Process ID")),
	), processExistsHandler)

	// process_kill
	mcpServer.AddTool(mcp.NewTool("process_kill",
		mcp.WithDescription("Kill process by PID"),
		mcp.WithNumber("pid", mcp.Required(), mcp.Description("Process ID")),
	), processKillHandler)

	// process_run
	mcpServer.AddTool(mcp.NewTool("process_run",
		mcp.WithDescription("Run shell command"),
		mcp.WithString("command", mcp.Required(), mcp.Description("Command to run")),
	), processRunHandler)
}

func registerSystemTools(mcpServer *server.MCPServer) {
	// system_get_info
	mcpServer.AddTool(mcp.NewTool("system_get_info",
		mcp.WithDescription("Get system information"),
	), systemGetInfoHandler)

	// util_sleep
	mcpServer.AddTool(mcp.NewTool("util_sleep",
		mcp.WithDescription("Sleep/pause for specified milliseconds"),
		mcp.WithNumber("milliseconds", mcp.Required(), mcp.Description("Milliseconds to sleep")),
	), utilSleepHandler)

	// alert_show
	mcpServer.AddTool(mcp.NewTool("alert_show",
		mcp.WithDescription("Show alert dialog"),
		mcp.WithString("title", mcp.Required(), mcp.Description("Dialog title")),
		mcp.WithString("message", mcp.Required(), mcp.Description("Dialog message")),
		mcp.WithString("default_btn", mcp.Description("Default button text (default: 'OK')")),
		mcp.WithString("cancel_btn", mcp.Description("Cancel button text (optional)")),
	), alertShowHandler)
}

func main() {
	// Parse command line arguments
	transport := flag.String("t", "sse", "Transport type: 'sse' or 'stdio'")
	host := flag.String("h", "0.0.0.0", "Host for SSE server")
	port := flag.Int("p", 8080, "Port for SSE server")
	flag.Parse()

	// Create MCP server
	mcpServer := server.NewMCPServer(ServerName, ServerVersion)

	// Register all tools
	registerMouseTools(mcpServer)
	registerKeyboardTools(mcpServer)
	registerScreenTools(mcpServer)
	registerWindowTools(mcpServer)
	registerProcessTools(mcpServer)
	registerSystemTools(mcpServer)

	log.Printf("Starting %s v%s", ServerName, ServerVersion)
	log.Printf("Transport: %s", *transport)

	// Start server based on transport type
	switch *transport {
	case "sse":
		addr := fmt.Sprintf("%s:%d", *host, *port)
		log.Printf("SSE server listening on %s", addr)
		sseServer := server.NewSSEServer(mcpServer)
		if err := sseServer.Start(addr); err != nil {
			log.Fatalf("Failed to start SSE server: %v", err)
		}
	case "stdio":
		log.Println("Starting stdio transport")
		if err := server.ServeStdio(mcpServer); err != nil {
			log.Fatalf("Failed to start stdio server: %v", err)
		}
	default:
		log.Fatalf("Unknown transport type: %s", *transport)
	}
}
