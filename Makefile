.PHONY: build build-linux build-windows build-darwin build-all run install deps clean

BINARY_NAME=go_computer_use_mcp_server
VERSION=1.0.0

# Build for current platform
build:
	go build -ldflags "-s -w" -o $(BINARY_NAME) .

# Build for Linux (amd64)
build-linux:
	GOOS=linux GOARCH=amd64 go build -ldflags "-s -w" -o $(BINARY_NAME)-linux-amd64 .

# Build for Linux (arm64)
build-linux-arm64:
	GOOS=linux GOARCH=arm64 go build -ldflags "-s -w" -o $(BINARY_NAME)-linux-arm64 .

# Build for Windows (amd64)
build-windows:
	GOOS=windows GOARCH=amd64 go build -ldflags "-s -w" -o $(BINARY_NAME)-windows-amd64.exe .

# Build for macOS (amd64)
build-darwin:
	GOOS=darwin GOARCH=amd64 go build -ldflags "-s -w" -o $(BINARY_NAME)-darwin-amd64 .

# Build for macOS (arm64 - Apple Silicon)
build-darwin-arm64:
	GOOS=darwin GOARCH=arm64 go build -ldflags "-s -w" -o $(BINARY_NAME)-darwin-arm64 .

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
	go install -ldflags "-s -w" .

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

# Show help
help:
	@echo "Available targets:"
	@echo "  build            - Build for current platform"
	@echo "  build-linux      - Build for Linux (amd64)"
	@echo "  build-linux-arm64- Build for Linux (arm64)"
	@echo "  build-windows    - Build for Windows (amd64)"
	@echo "  build-darwin     - Build for macOS (amd64)"
	@echo "  build-darwin-arm64 - Build for macOS (arm64)"
	@echo "  build-all        - Build for all platforms"
	@echo "  run              - Run SSE server on port 8080"
	@echo "  run-stdio        - Run with stdio transport"
	@echo "  install          - Install to GOPATH/bin"
	@echo "  deps             - Download dependencies"
	@echo "  clean            - Remove build artifacts"
