#!/usr/bin/env node
/**
 * Build commands for encapsulating other build scripts may will be required in the future.
 * For now, this script is a simple wrapper around the build commands.
 */
const { execSync } = require("child_process");

function runCommand(command) {
  console.log(`\n📦 Running: ${command}\n`);
  try {
    execSync(command, { stdio: "inherit", shell: true });
  } catch (error) {
    console.error(`\n❌ Command failed: ${command}`);
    process.exit(1);
  }
}

async function main() {
  console.log("\n🏗️  Building JavaScript and backend components...\n");
  runCommand("npm run build:js && npm run build:backends");

  console.log("\n✨ Build complete!\n");
}

main().catch((error) => {
  console.error("Build failed:", error);
  process.exit(1);
});
