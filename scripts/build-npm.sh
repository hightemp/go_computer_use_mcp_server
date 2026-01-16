#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/native"

mkdir -p "$OUT_DIR"

build_target() {
  local os="$1"
  local arch="$2"
  local ext="$3"
  local target_dir="$OUT_DIR/${os}-${arch}"
  local binary_name="go_computer_use_mcp_server-${os}-${arch}${ext}"

  mkdir -p "$target_dir"
  echo "Building ${os}/${arch}..."
  CGO_ENABLED=1 GOOS="$os" GOARCH="$arch" \
    go build -ldflags "-s -w" -o "$target_dir/$binary_name" "$ROOT_DIR"
}

# Note: CGO is required for robotgo library
# Cross-compilation with CGO requires appropriate cross-compilers
# For CI, we build only for the current platform or use Docker/QEMU

# Detect current platform
CURRENT_OS=$(go env GOOS)
CURRENT_ARCH=$(go env GOARCH)

echo "Building for current platform: ${CURRENT_OS}/${CURRENT_ARCH}"

case "$CURRENT_OS" in
  linux)
    build_target linux "$CURRENT_ARCH" ""
    ;;
  darwin)
    build_target darwin "$CURRENT_ARCH" ""
    ;;
  windows)
    build_target windows "$CURRENT_ARCH" ".exe"
    ;;
  *)
    echo "Unsupported OS: $CURRENT_OS"
    exit 1
    ;;
esac

echo "Done. Binaries are in $OUT_DIR"
