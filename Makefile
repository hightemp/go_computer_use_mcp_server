.PHONY: build build-linux build-windows build-darwin build-all run install deps clean \
        test test-system test-process test-screen test-mouse test-keyboard test-window test-no-gui \
        release sync-version

BINARY_NAME=go_computer_use_mcp_server
VERSION := $(shell cat VERSION | tr -d '[:space:]')
# Optional force flag — set to any non-empty value to force-overwrite the tag:
#   make release FORCE=1
FORCE ?=

LDFLAGS := -s -w -X main.ServerVersion=$(VERSION)

# Build for current platform
build:
	go build -ldflags "$(LDFLAGS)" -o $(BINARY_NAME) .

# Build for Linux (amd64)
build-linux:
	GOOS=linux GOARCH=amd64 go build -ldflags "$(LDFLAGS)" -o $(BINARY_NAME)-linux-amd64 .

# Build for Linux (arm64)
build-linux-arm64:
	GOOS=linux GOARCH=arm64 go build -ldflags "$(LDFLAGS)" -o $(BINARY_NAME)-linux-arm64 .

# Build for Windows (amd64)
build-windows:
	GOOS=windows GOARCH=amd64 go build -ldflags "$(LDFLAGS)" -o $(BINARY_NAME)-windows-amd64.exe .

# Build for macOS (amd64)
build-darwin:
	GOOS=darwin GOARCH=amd64 go build -ldflags "$(LDFLAGS)" -o $(BINARY_NAME)-darwin-amd64 .

# Build for macOS (arm64 - Apple Silicon)
build-darwin-arm64:
	GOOS=darwin GOARCH=arm64 go build -ldflags "$(LDFLAGS)" -o $(BINARY_NAME)-darwin-arm64 .

# Build for all platforms
build-all: build-linux build-linux-arm64 build-windows build-darwin build-darwin-arm64

# Run the server
run:
	go run . -t sse -h 0.0.0.0 -p 8080

# Run with stdio transport
run-stdio:
	go run . -t stdio

# Install to GOPATH/bin
install:
	go install -ldflags "$(LDFLAGS)" .

# Download dependencies
deps:
	go mod download
	go mod tidy

# Clean build artifacts
clean:
	rm -f $(BINARY_NAME)
	rm -f $(BINARY_NAME)-linux-amd64
	rm -f $(BINARY_NAME)-linux-arm64
	rm -f $(BINARY_NAME)-windows-amd64.exe
	rm -f $(BINARY_NAME)-darwin-amd64
	rm -f $(BINARY_NAME)-darwin-arm64

# ==================== Release ====================

# Read version from VERSION file, update package metadata, commit, tag, and push.
# Usage:
#   make release            — normal release  (fails if tag already exists)
#   make release FORCE=1    — force-overwrite existing tag
sync-version:
	@if [ -z "$(VERSION)" ]; then echo "ERROR: VERSION file is empty or missing"; exit 1; fi
	@node scripts/sync-version.js "$(VERSION)"
	@echo "Synced package.json and server.json to v$(VERSION)"

release: sync-version
	@echo "Releasing v$(VERSION) (FORCE=$(FORCE))..."
	@if ! git diff --quiet package.json server.json VERSION; then \
		git add package.json server.json VERSION; \
		git commit -m "chore: bump version to $(VERSION)"; \
	fi
	@if [ -n "$(FORCE)" ]; then \
		git tag -f v$(VERSION); \
		git push origin HEAD; \
		git push -f origin v$(VERSION); \
	else \
		git tag v$(VERSION); \
		git push origin HEAD; \
		git push origin v$(VERSION); \
	fi
	@echo "Done: v$(VERSION)"

# ==================== Tests ====================

# Run all tests
test: build
	python3 -m pytest tests/ -v

# Run all tests with short output
test-short: build
	python3 -m pytest tests/

# Run system tests
test-system: build
	python3 -m pytest tests/test_system.py -v

# Run process tests
test-process: build
	python3 -m pytest tests/test_process.py -v

# Run screen tests
test-screen: build
	python3 -m pytest tests/test_screen.py -v

# Run mouse tests
test-mouse: build
	python3 -m pytest tests/test_mouse.py -v

# Run keyboard tests
test-keyboard: build
	python3 -m pytest tests/test_keyboard.py -v

# Run window tests
test-window: build
	python3 -m pytest tests/test_window_tools.py -v

# Run tests without GUI (for headless environments)
test-no-gui: build
	python3 -m pytest tests/ -v -m "not gui"

# Show help
help:
	@echo "Available targets:"
	@echo ""
	@echo "Build:"
	@echo "  build              - Build for current platform"
	@echo "  build-linux        - Build for Linux (amd64)"
	@echo "  build-linux-arm64  - Build for Linux (arm64)"
	@echo "  build-windows      - Build for Windows (amd64)"
	@echo "  build-darwin       - Build for macOS (amd64)"
	@echo "  build-darwin-arm64 - Build for macOS (arm64)"
	@echo "  build-all          - Build for all platforms"
	@echo ""
	@echo "Run:"
	@echo "  run                - Run SSE server on port 8080"
	@echo "  run-stdio          - Run with stdio transport"
	@echo ""
	@echo "Tests:"
	@echo "  test               - Run all tests (verbose)"
	@echo "  test-short         - Run all tests (short output)"
	@echo "  test-system        - Run system tests only"
	@echo "  test-process       - Run process tests only"
	@echo "  test-screen        - Run screen tests only"
	@echo "  test-mouse         - Run mouse tests only"
	@echo "  test-keyboard      - Run keyboard tests only"
	@echo "  test-window        - Run window tests only"
	@echo "  test-no-gui        - Run tests without GUI (headless)"
	@echo ""
	@echo "Other:"
	@echo "  install            - Install to GOPATH/bin"
	@echo "  deps               - Download dependencies"
	@echo "  clean              - Remove build artifacts"
	@echo ""
	@echo "Release (version is read from the VERSION file):"
	@echo "  sync-version       - Update package.json and server.json from VERSION"
	@echo "  release            - Update package.json/server.json, tag vX.Y.Z, push"
	@echo "  release FORCE=1    - Same but force-overwrites an existing tag"
