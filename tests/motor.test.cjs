"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");

function createTempMemoryDir() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "takios-memory-"));
  fs.mkdirSync(path.join(dir, "archive"), { recursive: true });
  return dir;
}

function writeJson(filePath, data) {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), "utf-8");
}

function loadMotor(memoryDir) {
  process.env.TAKIOS_MEMORY_DIR = memoryDir;
  delete require.cache[require.resolve("../bin/lib/motor.cjs")];
  return require("../bin/lib/motor.cjs");
}

test("compacts sessions and archives processed files", async () => {
  const memoryDir = createTempMemoryDir();
  writeJson(path.join(memoryDir, "motor.json"), {
    dreamIntervalMs: 1,
    checkIntervalMs: 1,
    sessionThreshold: 1,
    maxIndexLines: 200,
    maxLineChars: 120,
    logLevel: "error"
  });

  const sessionFile = path.join(memoryDir, "session-1.json");
  writeJson(sessionFile, {
    session_id: "s1",
    entries: [
      { content: "ok", category: "general" },
      { content: "Adopt EventBus for cross-layer communication", category: "architecture" }
    ]
  });

  const motor = loadMotor(memoryDir);
  const result = await motor.executeDreamCycle("test");

  assert.equal(result.status, "completed");
  assert.ok(fs.existsSync(path.join(memoryDir, "context.mmd")));
  assert.ok(fs.existsSync(path.join(memoryDir, "archive", "session-1.json")));

  const index = fs.readFileSync(path.join(memoryDir, "context.mmd"), "utf-8");
  assert.match(index, /\[architecture\]/);
  assert.equal(fs.existsSync(path.join(memoryDir, "motor_state.json")), true);
});

test("archives invalid sessions into archive/invalid", async () => {
  const memoryDir = createTempMemoryDir();
  writeJson(path.join(memoryDir, "motor.json"), {
    dreamIntervalMs: 1,
    checkIntervalMs: 1,
    sessionThreshold: 1,
    maxIndexLines: 200,
    maxLineChars: 120,
    logLevel: "error"
  });

  const invalidFile = path.join(memoryDir, "session-invalid.json");
  fs.writeFileSync(invalidFile, "{not-json}", "utf-8");

  const motor = loadMotor(memoryDir);
  const result = await motor.executeDreamCycle("test");

  assert.equal(result.status, "completed");
  assert.ok(
    fs.existsSync(path.join(memoryDir, "archive", "invalid", "session-invalid.json"))
  );
});

test("handles empty memory directory gracefully", async () => {
  const memoryDir = createTempMemoryDir();
  writeJson(path.join(memoryDir, "motor.json"), {
    dreamIntervalMs: 1,
    checkIntervalMs: 1,
    sessionThreshold: 0,
    maxIndexLines: 200,
    maxLineChars: 120,
    logLevel: "error"
  });

  const motor = loadMotor(memoryDir);
  const result = await motor.executeDreamCycle("test");

  assert.equal(result.status, "completed");
});

test("respects maxIndexLines limit", async () => {
  const memoryDir = createTempMemoryDir();
  const maxLines = 5;
  writeJson(path.join(memoryDir, "motor.json"), {
    dreamIntervalMs: 1,
    checkIntervalMs: 1,
    sessionThreshold: 1,
    maxIndexLines: maxLines,
    maxLineChars: 120,
    logLevel: "error"
  });

  // Create sessions with many entries to exceed the limit
  const entries = [];
  for (let i = 0; i < 20; i++) {
    entries.push({ content: `Architecture decision number ${i} about layer ${i % 13}`, category: "architecture" });
  }
  writeJson(path.join(memoryDir, "session-big.json"), {
    session_id: "s-big",
    entries
  });

  const motor = loadMotor(memoryDir);
  await motor.executeDreamCycle("test");

  const index = fs.readFileSync(path.join(memoryDir, "context.mmd"), "utf-8");
  const lines = index.trim().split("\n").filter(Boolean);
  assert.ok(lines.length <= maxLines, `Expected <= ${maxLines} lines, got ${lines.length}`);
});

test("filters filler entries from sessions", async () => {
  const memoryDir = createTempMemoryDir();
  writeJson(path.join(memoryDir, "motor.json"), {
    dreamIntervalMs: 1,
    checkIntervalMs: 1,
    sessionThreshold: 1,
    maxIndexLines: 200,
    maxLineChars: 120,
    logLevel: "error"
  });

  writeJson(path.join(memoryDir, "session-filler.json"), {
    session_id: "s-filler",
    entries: [
      { content: "ok", category: "general" },
      { content: "sure", category: "general" },
      { content: "got it", category: "general" },
      { content: "thanks", category: "general" },
      { content: "[error] Redis connection refused on port 6379 — switched to failopen", category: "error" }
    ]
  });

  const motor = loadMotor(memoryDir);
  await motor.executeDreamCycle("test");

  const index = fs.readFileSync(path.join(memoryDir, "context.mmd"), "utf-8");
  // Filler should be pruned, but the error entry should be preserved
  assert.match(index, /\[error\]/);
  assert.doesNotMatch(index, /\bgot it\b/i);
});

test("preserves existing index when appending new entries", async () => {
  const memoryDir = createTempMemoryDir();
  writeJson(path.join(memoryDir, "motor.json"), {
    dreamIntervalMs: 1,
    checkIntervalMs: 1,
    sessionThreshold: 1,
    maxIndexLines: 200,
    maxLineChars: 120,
    logLevel: "error"
  });

  // Pre-populate context.mmd
  fs.writeFileSync(
    path.join(memoryDir, "context.mmd"),
    "[decision] Use FastAPI with async SQLAlchemy 2\n",
    "utf-8"
  );

  writeJson(path.join(memoryDir, "session-new.json"), {
    session_id: "s-new",
    entries: [
      { content: "Added pgvector extension for semantic search", category: "architecture" }
    ]
  });

  const motor = loadMotor(memoryDir);
  await motor.executeDreamCycle("test");

  const index = fs.readFileSync(path.join(memoryDir, "context.mmd"), "utf-8");
  assert.match(index, /FastAPI/);
  assert.match(index, /pgvector|semantic/i);
});
