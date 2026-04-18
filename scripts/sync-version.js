#!/usr/bin/env node

const fs = require("node:fs");

const version = process.argv[2];

if (!version) {
  console.error("Usage: node scripts/sync-version.js <version>");
  process.exit(1);
}

function readJson(path) {
  return JSON.parse(fs.readFileSync(path, "utf8"));
}

function writeJson(path, data) {
  fs.writeFileSync(path, `${JSON.stringify(data, null, 2)}\n`);
}

const packageJson = readJson("package.json");
packageJson.version = version;
writeJson("package.json", packageJson);

const serverJson = readJson("server.json");
serverJson.version = version;

for (const packageEntry of serverJson.packages ?? []) {
  packageEntry.version = version;
}

writeJson("server.json", serverJson);
