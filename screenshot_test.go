package main

import (
	"encoding/base64"
	"fmt"
	"image"
	"image/color"
	"image/png"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/hightemp/robotgo"
)

// TestScreenshotBasic tests basic screenshot functionality
func TestScreenshotBasic(t *testing.T) {
	t.Log("Testing basic screenshot capture...")

	img, err := robotgo.CaptureImg()
	if err != nil {
		t.Fatalf("Failed to capture screenshot: %v", err)
	}

	if img == nil {
		t.Fatal("CaptureImg returned nil image")
	}

	bounds := img.Bounds()
	t.Logf("Captured image size: %dx%d", bounds.Dx(), bounds.Dy())

	if bounds.Dx() == 0 || bounds.Dy() == 0 {
		t.Fatal("Image has zero dimensions")
	}
}

// TestScreenshotNotBlack verifies that screenshot is not completely black
func TestScreenshotNotBlack(t *testing.T) {
	t.Log("Testing that screenshot is not black...")

	img, err := robotgo.CaptureImg()
	if err != nil {
		t.Fatalf("Failed to capture screenshot: %v", err)
	}

	bounds := img.Bounds()
	blackPixels := 0
	totalPixels := 0
	nonBlackPixels := 0

	// Sample pixels across the image
	for y := bounds.Min.Y; y < bounds.Max.Y; y += 10 {
		for x := bounds.Min.X; x < bounds.Max.X; x += 10 {
			totalPixels++
			r, g, b, a := img.At(x, y).RGBA()
			// RGBA returns values in range 0-65535
			if r == 0 && g == 0 && b == 0 {
				blackPixels++
			} else {
				nonBlackPixels++
			}
			// Log first few non-black pixels for debugging
			if nonBlackPixels <= 5 && (r > 0 || g > 0 || b > 0) {
				t.Logf("Non-black pixel at (%d,%d): R=%d G=%d B=%d A=%d", x, y, r>>8, g>>8, b>>8, a>>8)
			}
		}
	}

	blackPercent := float64(blackPixels) / float64(totalPixels) * 100
	t.Logf("Black pixels: %d/%d (%.1f%%)", blackPixels, totalPixels, blackPercent)

	if blackPercent > 99.0 {
		t.Errorf("Screenshot appears to be completely black (%.1f%% black pixels)", blackPercent)
	}
}

// TestScreenshotWithDisplayID tests screenshot with specific display ID
func TestScreenshotWithDisplayID(t *testing.T) {
	numDisplays := robotgo.DisplaysNum()
	t.Logf("Number of displays: %d", numDisplays)

	// Test display_id = -1 (default)
	t.Run("DisplayID_-1", func(t *testing.T) {
		robotgo.DisplayID = -1
		img, err := robotgo.CaptureImg()
		if err != nil {
			t.Fatalf("Failed with display_id=-1: %v", err)
		}
		bounds := img.Bounds()
		t.Logf("display_id=-1: %dx%d", bounds.Dx(), bounds.Dy())
		checkNotBlack(t, img, "display_id=-1")
	})

	// Test display_id = 0
	t.Run("DisplayID_0", func(t *testing.T) {
		robotgo.DisplayID = 0
		defer func() { robotgo.DisplayID = -1 }()

		img, err := robotgo.CaptureImg()
		if err != nil {
			t.Fatalf("Failed with display_id=0: %v", err)
		}
		bounds := img.Bounds()
		t.Logf("display_id=0: %dx%d", bounds.Dx(), bounds.Dy())
		checkNotBlack(t, img, "display_id=0")
	})

	// Test each available display
	for i := 0; i < numDisplays; i++ {
		t.Run(fmt.Sprintf("DisplayID_%d", i), func(t *testing.T) {
			robotgo.DisplayID = i
			defer func() { robotgo.DisplayID = -1 }()

			x, y, w, h := robotgo.GetDisplayBounds(i)
			t.Logf("Display %d bounds: pos(%d,%d) size(%dx%d)", i, x, y, w, h)

			img, err := robotgo.CaptureImg()
			if err != nil {
				t.Fatalf("Failed with display_id=%d: %v", i, err)
			}
			bounds := img.Bounds()
			t.Logf("display_id=%d: captured %dx%d", i, bounds.Dx(), bounds.Dy())
			checkNotBlack(t, img, fmt.Sprintf("display_id=%d", i))
		})
	}
}

// TestScreenshotMultipleCaptures tests multiple sequential captures
func TestScreenshotMultipleCaptures(t *testing.T) {
	t.Log("Testing multiple sequential captures...")

	for i := 0; i < 5; i++ {
		robotgo.DisplayID = 0
		img, err := robotgo.CaptureImg()
		robotgo.DisplayID = -1

		if err != nil {
			t.Fatalf("Capture %d failed: %v", i+1, err)
		}

		bounds := img.Bounds()
		t.Logf("Capture %d: %dx%d", i+1, bounds.Dx(), bounds.Dy())
	}
}

// TestScreenshotRegion tests capturing a specific region
func TestScreenshotRegion(t *testing.T) {
	t.Log("Testing region capture...")

	// Capture 100x100 region at position 100,100
	img, err := robotgo.CaptureImg(100, 100, 100, 100)
	if err != nil {
		t.Fatalf("Failed to capture region: %v", err)
	}

	bounds := img.Bounds()
	t.Logf("Region capture: %dx%d", bounds.Dx(), bounds.Dy())

	if bounds.Dx() != 100 || bounds.Dy() != 100 {
		t.Errorf("Expected 100x100, got %dx%d", bounds.Dx(), bounds.Dy())
	}

	checkNotBlack(t, img, "region capture")
}

// TestScreenshotPNGEncode tests PNG encoding of screenshot
func TestScreenshotPNGEncode(t *testing.T) {
	t.Log("Testing PNG encoding...")

	img, err := robotgo.CaptureImg()
	if err != nil {
		t.Fatalf("Failed to capture: %v", err)
	}

	// Create temp file
	tmpDir := t.TempDir()
	tmpFile := filepath.Join(tmpDir, "test_screenshot.png")

	f, err := os.Create(tmpFile)
	if err != nil {
		t.Fatalf("Failed to create temp file: %v", err)
	}

	err = png.Encode(f, img)
	f.Close()
	if err != nil {
		t.Fatalf("Failed to encode PNG: %v", err)
	}

	// Check file size
	info, err := os.Stat(tmpFile)
	if err != nil {
		t.Fatalf("Failed to stat file: %v", err)
	}

	t.Logf("PNG file size: %d bytes", info.Size())

	if info.Size() < 100 {
		t.Error("PNG file seems too small, might be corrupted or black")
	}

	// Read back and verify
	f, err = os.Open(tmpFile)
	if err != nil {
		t.Fatalf("Failed to open file: %v", err)
	}
	defer f.Close()

	decodedImg, err := png.Decode(f)
	if err != nil {
		t.Fatalf("Failed to decode PNG: %v", err)
	}

	checkNotBlack(t, decodedImg, "decoded PNG")
}

// TestScreenshotBase64 tests base64 encoding (as used by MCP)
func TestScreenshotBase64(t *testing.T) {
	t.Log("Testing base64 encoding (MCP format)...")

	img, err := robotgo.CaptureImg()
	if err != nil {
		t.Fatalf("Failed to capture: %v", err)
	}

	// Encode to PNG bytes
	var buf strings.Builder
	encoder := base64.NewEncoder(base64.StdEncoding, &buf)

	// We need to write PNG to a buffer first
	tmpDir := t.TempDir()
	tmpFile := filepath.Join(tmpDir, "test.png")

	f, _ := os.Create(tmpFile)
	png.Encode(f, img)
	f.Close()

	// Read and base64 encode
	data, _ := os.ReadFile(tmpFile)
	base64Str := base64.StdEncoding.EncodeToString(data)
	encoder.Close()

	t.Logf("Base64 string length: %d", len(base64Str))

	// Verify it can be decoded
	decoded, err := base64.StdEncoding.DecodeString(base64Str)
	if err != nil {
		t.Fatalf("Failed to decode base64: %v", err)
	}

	t.Logf("Decoded bytes: %d", len(decoded))

	// Check PNG header
	if len(decoded) < 8 {
		t.Fatal("Decoded data too short")
	}

	pngHeader := []byte{0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A}
	for i, b := range pngHeader {
		if decoded[i] != b {
			t.Errorf("Invalid PNG header at byte %d: expected 0x%02X, got 0x%02X", i, b, decoded[i])
		}
	}
	t.Log("PNG header is valid")
}

// TestScreenshotColorAnalysis analyzes color distribution in screenshot
func TestScreenshotColorAnalysis(t *testing.T) {
	t.Log("Analyzing screenshot color distribution...")

	img, err := robotgo.CaptureImg()
	if err != nil {
		t.Fatalf("Failed to capture: %v", err)
	}

	bounds := img.Bounds()
	colorCounts := make(map[string]int)
	totalSamples := 0

	// Sample pixels
	for y := bounds.Min.Y; y < bounds.Max.Y; y += 50 {
		for x := bounds.Min.X; x < bounds.Max.X; x += 50 {
			totalSamples++
			r, g, b, _ := img.At(x, y).RGBA()
			// Categorize colors
			r8, g8, b8 := r>>8, g>>8, b>>8

			var category string
			if r8 == 0 && g8 == 0 && b8 == 0 {
				category = "black"
			} else if r8 == 255 && g8 == 255 && b8 == 255 {
				category = "white"
			} else if r8 > 200 && g8 > 200 && b8 > 200 {
				category = "light"
			} else if r8 < 50 && g8 < 50 && b8 < 50 {
				category = "dark"
			} else {
				category = "colored"
			}
			colorCounts[category]++
		}
	}

	t.Logf("Color distribution (total samples: %d):", totalSamples)
	for cat, count := range colorCounts {
		percent := float64(count) / float64(totalSamples) * 100
		t.Logf("  %s: %d (%.1f%%)", cat, count, percent)
	}

	// Warn if mostly black
	blackPercent := float64(colorCounts["black"]) / float64(totalSamples) * 100
	if blackPercent > 90 {
		t.Errorf("WARNING: Screenshot is %.1f%% black!", blackPercent)
	}
}

// TestScreenshotSaveAndVerify saves screenshot and verifies it's viewable
func TestScreenshotSaveAndVerify(t *testing.T) {
	t.Log("Saving screenshot for manual verification...")

	img, err := robotgo.CaptureImg()
	if err != nil {
		t.Fatalf("Failed to capture: %v", err)
	}

	// Save to project directory for inspection
	outputPath := "/tmp/mcp_screenshot_test.png"
	f, err := os.Create(outputPath)
	if err != nil {
		t.Fatalf("Failed to create file: %v", err)
	}

	err = png.Encode(f, img)
	f.Close()
	if err != nil {
		t.Fatalf("Failed to encode: %v", err)
	}

	info, _ := os.Stat(outputPath)
	t.Logf("Screenshot saved to: %s (size: %d bytes)", outputPath, info.Size())
	t.Log("Please verify this screenshot manually!")

	checkNotBlack(t, img, "saved screenshot")
}

// TestXDisplayEnvironment checks X11 display environment
func TestXDisplayEnvironment(t *testing.T) {
	display := os.Getenv("DISPLAY")
	t.Logf("DISPLAY environment variable: %q", display)

	if display == "" {
		t.Error("DISPLAY environment variable is not set!")
	}

	// Check XDG_SESSION_TYPE
	sessionType := os.Getenv("XDG_SESSION_TYPE")
	t.Logf("XDG_SESSION_TYPE: %q", sessionType)

	// Check WAYLAND_DISPLAY
	waylandDisplay := os.Getenv("WAYLAND_DISPLAY")
	t.Logf("WAYLAND_DISPLAY: %q", waylandDisplay)

	if waylandDisplay != "" && sessionType == "wayland" {
		t.Log("WARNING: Running under Wayland! X11 screenshot may not work correctly.")
	}
}

// Helper function to check if image is not black
func checkNotBlack(t *testing.T, img image.Image, context string) {
	t.Helper()

	bounds := img.Bounds()
	blackPixels := 0
	totalPixels := 0

	for y := bounds.Min.Y; y < bounds.Max.Y; y += 20 {
		for x := bounds.Min.X; x < bounds.Max.X; x += 20 {
			totalPixels++
			r, g, b, _ := img.At(x, y).RGBA()
			if r == 0 && g == 0 && b == 0 {
				blackPixels++
			}
		}
	}

	blackPercent := float64(blackPixels) / float64(totalPixels) * 100
	if blackPercent > 95 {
		t.Errorf("[%s] Image is %.1f%% black (likely broken)", context, blackPercent)
	} else {
		t.Logf("[%s] Image OK - %.1f%% non-black pixels", context, 100-blackPercent)
	}
}

// TestPixelColorDirect tests direct pixel color reading
func TestPixelColorDirect(t *testing.T) {
	t.Log("Testing direct pixel color reading...")

	// Get color at center of screen
	w, h := robotgo.GetScreenSize()
	centerX, centerY := w/2, h/2

	color := robotgo.GetPixelColor(centerX, centerY)
	t.Logf("Pixel color at (%d,%d): #%s", centerX, centerY, color)

	if color == "000000" {
		t.Log("WARNING: Center pixel is black")
	}

	// Get mouse position color
	mouseColor := robotgo.GetLocationColor()
	t.Logf("Pixel color at mouse position: #%s", mouseColor)
}

// TestRobotgoVersion prints robotgo version info
func TestRobotgoVersion(t *testing.T) {
	version := robotgo.GetVersion()
	t.Logf("Robotgo version: %s", version)

	// Get screen info
	w, h := robotgo.GetScreenSize()
	t.Logf("Screen size: %dx%d", w, h)

	numDisplays := robotgo.DisplaysNum()
	t.Logf("Number of displays: %d", numDisplays)

	for i := 0; i < numDisplays; i++ {
		x, y, w, h := robotgo.GetDisplayBounds(i)
		t.Logf("Display %d: pos(%d,%d) size(%dx%d)", i, x, y, w, h)
	}
}

// BenchmarkScreenshot benchmarks screenshot performance
func BenchmarkScreenshot(b *testing.B) {
	for i := 0; i < b.N; i++ {
		img, err := robotgo.CaptureImg()
		if err != nil {
			b.Fatal(err)
		}
		_ = img
	}
}

// TestAlternativeCaptureMethods tests different capture approaches
func TestAlternativeCaptureMethods(t *testing.T) {
	t.Log("Testing alternative capture methods...")

	// Method 1: CaptureImg (default)
	t.Run("CaptureImg", func(t *testing.T) {
		img, err := robotgo.CaptureImg()
		if err != nil {
			t.Fatalf("CaptureImg failed: %v", err)
		}
		bounds := img.Bounds()
		t.Logf("CaptureImg: %dx%d", bounds.Dx(), bounds.Dy())
		checkNotBlack(t, img, "CaptureImg")
	})

	// Method 2: CaptureScreen + ToImage
	t.Run("CaptureScreen", func(t *testing.T) {
		bit := robotgo.CaptureScreen()
		if bit == nil {
			t.Fatal("CaptureScreen returned nil")
		}
		defer robotgo.FreeBitmap(bit)

		img := robotgo.ToImage(bit)
		if img == nil {
			t.Fatal("ToImage returned nil")
		}
		bounds := img.Bounds()
		t.Logf("CaptureScreen+ToImage: %dx%d", bounds.Dx(), bounds.Dy())
		checkNotBlack(t, img, "CaptureScreen")
	})

	// Method 3: SaveCapture (saves directly to file)
	t.Run("SaveCapture", func(t *testing.T) {
		tmpFile := "/tmp/robotgo_savecapture_test.png"
		err := robotgo.SaveCapture(tmpFile)
		if err != nil {
			t.Fatalf("SaveCapture failed: %v", err)
		}

		// Read back and verify
		f, err := os.Open(tmpFile)
		if err != nil {
			t.Fatalf("Failed to open saved file: %v", err)
		}
		defer f.Close()

		img, err := png.Decode(f)
		if err != nil {
			t.Fatalf("Failed to decode saved PNG: %v", err)
		}

		bounds := img.Bounds()
		t.Logf("SaveCapture: %dx%d", bounds.Dx(), bounds.Dy())
		checkNotBlack(t, img, "SaveCapture")

		os.Remove(tmpFile)
	})
}

// TestImagePixelValues inspects actual pixel values
func TestImagePixelValues(t *testing.T) {
	t.Log("Inspecting pixel values...")

	img, err := robotgo.CaptureImg()
	if err != nil {
		t.Fatalf("Failed to capture: %v", err)
	}

	bounds := img.Bounds()

	// Check corners and center
	positions := []struct {
		name string
		x, y int
	}{
		{"top-left", bounds.Min.X, bounds.Min.Y},
		{"top-right", bounds.Max.X - 1, bounds.Min.Y},
		{"bottom-left", bounds.Min.X, bounds.Max.Y - 1},
		{"bottom-right", bounds.Max.X - 1, bounds.Max.Y - 1},
		{"center", (bounds.Min.X + bounds.Max.X) / 2, (bounds.Min.Y + bounds.Max.Y) / 2},
	}

	for _, pos := range positions {
		c := img.At(pos.x, pos.y)
		r, g, b, a := c.RGBA()
		t.Logf("%s (%d,%d): RGBA(%d,%d,%d,%d) raw=%v",
			pos.name, pos.x, pos.y, r>>8, g>>8, b>>8, a>>8, c)
	}

	// Check image type
	t.Logf("Image type: %T", img)

	// If it's RGBA, check underlying data
	if rgba, ok := img.(*image.RGBA); ok {
		t.Logf("RGBA stride: %d, bounds: %v", rgba.Stride, rgba.Bounds())
		// Check first few bytes
		if len(rgba.Pix) > 16 {
			t.Logf("First 16 bytes: %v", rgba.Pix[:16])
		}
	} else if nrgba, ok := img.(*image.NRGBA); ok {
		t.Logf("NRGBA stride: %d, bounds: %v", nrgba.Stride, nrgba.Bounds())
		if len(nrgba.Pix) > 16 {
			t.Logf("First 16 bytes: %v", nrgba.Pix[:16])
		}
	}
}

// TestColorModel checks color model of captured image
func TestColorModel(t *testing.T) {
	img, err := robotgo.CaptureImg()
	if err != nil {
		t.Fatalf("Failed: %v", err)
	}

	cm := img.ColorModel()
	t.Logf("Color model: %v", cm)

	// Convert a known color to see model behavior
	testColors := []color.Color{
		color.RGBA{255, 0, 0, 255},
		color.RGBA{0, 255, 0, 255},
		color.RGBA{0, 0, 255, 255},
		color.RGBA{255, 255, 255, 255},
		color.RGBA{0, 0, 0, 255},
	}

	for _, c := range testColors {
		converted := cm.Convert(c)
		r, g, b, a := converted.RGBA()
		t.Logf("Input %v -> Output RGBA(%d,%d,%d,%d)", c, r>>8, g>>8, b>>8, a>>8)
	}
}
