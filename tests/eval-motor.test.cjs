"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");

const REPO_ROOT = path.resolve(__dirname, "..");
const CONFIG_PATH = path.join(REPO_ROOT, "config", "eval-motor.json");
const TARGET_PATH = path.join(REPO_ROOT, "skills", "target_skill.md");
const MEMORY_DIR = path.join(REPO_ROOT, "memory");
const STATE_PATH = path.join(MEMORY_DIR, "eval-motor-state.json");
const LOCK_PATH = path.join(MEMORY_DIR, "eval-motor.lock");

function clearModule() {
  delete require.cache[require.resolve("../bin/lib/eval-motor.cjs")];
  return require("../bin/lib/eval-motor.cjs");
}

function read(filePath) {
  return fs.readFileSync(filePath, "utf-8");
}

function write(filePath, content) {
  fs.writeFileSync(filePath, content, "utf-8");
}

const originalConfig = read(CONFIG_PATH);
const originalTarget = read(TARGET_PATH);

test.afterEach(() => {
  write(CONFIG_PATH, originalConfig);
  write(TARGET_PATH, originalTarget);

  if (fs.existsSync(STATE_PATH)) {
    fs.unlinkSync(STATE_PATH);
  }
  if (fs.existsSync(LOCK_PATH)) {
    fs.unlinkSync(LOCK_PATH);
  }
});

test("aggregateScores returns median/mode/passRate", () => {
  const motor = clearModule();
  const aggregate = motor.aggregateScores([1, 0, 1, 1, 0]);

  assert.equal(aggregate.passRate, 0.6);
  assert.equal(aggregate.median, 1);
  assert.equal(aggregate.mode, 1);
  assert.ok(aggregate.confidenceDelta > 0);
});

test("runOnce dry-run works with placeholders", async () => {
  const motor = clearModule();
  const result = await motor.runOnce({ dryRun: true });
  assert.equal(result.status, "dry_run");
  assert.equal(typeof result.config.passCount, "number");
});

test("runOnce executes one cycle with deterministic measurement", async () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "takios-eval-motor-"));
  const measurementScript = path.join(tempDir, "measurement.cjs");
  write(
    measurementScript,
    [
      '"use strict";',
      "process.stdout.write('PASS');",
      "",
    ].join("\n")
  );

  const config = {
    checkIntervalMs: 100,
    passCount: 3,
    targetMetric: 1,
    maxMutations: 2,
    mutationCooldownMs: 0,
    measurement: {
      command: process.execPath,
      args: [measurementScript],
      cwd: ".",
    },
    evaluator: {
      command: "<evaluator_command>",
      args: ["<evaluator_arg_1>"],
    },
    mutator: {
      command: "<mutator_command>",
      args: ["<mutator_arg_1>"],
    },
    targetFilePath: "skills/target_skill.md",
    logLevel: "error",
  };
  write(CONFIG_PATH, JSON.stringify(config, null, 2));

  const motor = clearModule();
  const result = await motor.runOnce();

  assert.equal(result.status, "target_met");
  assert.equal(result.aggregate.passRate, 1);
  assert.deepEqual(result.scores, [1, 1, 1]);
});

test("runOnce returns invalid_config when required placeholders remain", async () => {
  const config = {
    passCount: 3,
    targetMetric: 1,
    maxMutations: 2,
    mutationCooldownMs: 0,
    measurement: {
      command: "<measurement_tool_command>",
      args: ["<measurement_tool_arg_1>"],
      cwd: ".",
    },
    targetFilePath: "skills/target_skill.md",
    logLevel: "error",
  };
  write(CONFIG_PATH, JSON.stringify(config, null, 2));

  const motor = clearModule();
  const result = await motor.runOnce();

  assert.equal(result.status, "invalid_config");
  assert.ok(Array.isArray(result.errors));
  assert.ok(result.errors.length >= 1);
});

test("parseMutatorOutput supports JSON and raw text", () => {
  const motor = clearModule();

  const parsedJson = motor.parseMutatorOutput(
    JSON.stringify({ hypothesis: "h1", content: "new-content" }),
    "fallback",
    "fallback-h"
  );
  assert.equal(parsedJson.hypothesis, "h1");
  assert.equal(parsedJson.content, "new-content");
  assert.equal(parsedJson.mode, "command_json");

  const parsedRaw = motor.parseMutatorOutput("raw-content", "fallback", "fallback-h");
  assert.equal(parsedRaw.hypothesis, "fallback-h");
  assert.equal(parsedRaw.content, "raw-content");
  assert.equal(parsedRaw.mode, "command_raw");
});

test("executeEvalCycle rolls back when score regresses below baseline", async () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "takios-eval-rollback-"));
  const measurementScript = path.join(tempDir, "measurement-fail.cjs");
  write(
    measurementScript,
    [
      '"use strict";',
      "process.stdout.write('FAIL');",
      "",
    ].join("\n")
  );

  const backupPath = path.join(tempDir, "target.backup");
  write(backupPath, originalTarget);
  write(TARGET_PATH, "MUTATED CONTENT");

  const config = {
    passCount: 1,
    targetMetric: 1,
    maxMutations: 1,
    mutationCooldownMs: 0,
    commandTimeoutMs: 5000,
    rollbackOnRegression: true,
    minImprovementEpsilon: 0.001,
    measurement: {
      command: process.execPath,
      args: [measurementScript],
      cwd: ".",
    },
    evaluator: {
      command: "<evaluator_command>",
      args: ["<evaluator_arg_1>"],
    },
    mutator: {
      command: "<mutator_command>",
      args: ["<mutator_arg_1>"],
    },
    targetFilePath: "skills/target_skill.md",
    logLevel: "error",
  };

  const motor = clearModule();
  const result = await motor.executeEvalCycle(config, {
    cycles: 1,
    mutations: 1,
    lastPassRate: 0.8,
    pendingRollback: {
      backupPath,
      baselinePassRate: 0.8,
      cycleNumber: 1,
    },
  });

  assert.equal(result.rolledBack, true);
  assert.equal(result.status, "max_mutations_reached");
  assert.equal(read(TARGET_PATH), originalTarget);
});
