#!/usr/bin/env node

const { spawn } = require("node:child_process");
const { existsSync } = require("node:fs");
const { join } = require("node:path");

function resolveBinaryPath() {
  const platform = process.platform;
  const arch = process.arch;

  let platformKey = "";
  if (platform === "linux") {
    platformKey = "linux";
  } else if (platform === "darwin") {
    platformKey = "darwin";
  } else if (platform === "win32") {
    platformKey = "windows";
  }

  let archKey = "";
  if (arch === "x64") {
    archKey = "amd64";
  } else if (arch === "arm64") {
    archKey = "arm64";
  }

  if (!platformKey || !archKey) {
    throw new Error(`Unsupported platform/arch: ${platform}/${arch}`);
  }

  const binaryName = platformKey === "windows"
    ? `go_computer_use_mcp_server-${platformKey}-${archKey}.exe`
    : `go_computer_use_mcp_server-${platformKey}-${archKey}`;

  return join(__dirname, "..", "native", `${platformKey}-${archKey}`, binaryName);
}

function main() {
  let binaryPath;
  try {
    binaryPath = resolveBinaryPath();
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }

  if (!existsSync(binaryPath)) {
    console.error(`Binary not found: ${binaryPath}`);
    console.error("Run 'npm run build:npm' to generate platform binaries.");
    process.exit(1);
  }

  const child = spawn(binaryPath, process.argv.slice(2), {
    stdio: "inherit",
  });

  child.on("exit", (code, signal) => {
    if (signal) {
      process.kill(process.pid, signal);
      return;
    }
    process.exit(code ?? 0);
  });
}

main();
