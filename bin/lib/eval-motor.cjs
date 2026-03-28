"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { randomUUID } = require("node:crypto");
const { execFileSync } = require("node:child_process");

const ROOT_DIR = path.resolve(__dirname, "..", "..");
const MEMORY_DIR = path.join(ROOT_DIR, "memory");
const CONFIG_PATH = path.join(ROOT_DIR, "config", "eval-motor.json");
const LOG_PATH = path.join(MEMORY_DIR, "eval-motor.log");
const STATE_PATH = path.join(MEMORY_DIR, "eval-motor-state.json");
const STATE_TMP_PATH = path.join(MEMORY_DIR, "eval-motor-state.json.tmp");
const LOCK_PATH = path.join(MEMORY_DIR, "eval-motor.lock");
const MUTATION_LOG_PATH = path.join(MEMORY_DIR, "mutation_log.mmd");

const LOG_LEVELS = { debug: 0, info: 1, warn: 2, error: 3 };
let currentLogLevel = "info";

function log(level, message, meta = {}) {
  if (LOG_LEVELS[level] < LOG_LEVELS[currentLogLevel]) {
    return;
  }

  const entry = {
    timestamp: new Date().toISOString(),
    level,
    component: "eval-motor.cjs",
    message,
    ...meta,
  };
  const line = JSON.stringify(entry);

  if (level === "error") {
    process.stderr.write(line + "\n");
  } else {
    process.stdout.write(line + "\n");
  }

  try {
    fs.appendFileSync(LOG_PATH, line + "\n", "utf-8");
  } catch (_) {
    // Logging should never crash the motor.
  }
}

function ensureMemoryFiles() {
  fs.mkdirSync(MEMORY_DIR, { recursive: true });
  if (!fs.existsSync(MUTATION_LOG_PATH)) {
    fs.writeFileSync(
      MUTATION_LOG_PATH,
      "# Mutation Log - Auto-Research Motor\n# Format: [CYCLE] hypothesis | score_before -> score_after | status\n\n",
      "utf-8"
    );
  }
}

function hasPlaceholder(value) {
  return typeof value === "string" && /<[^>]+>/.test(value);
}

function loadConfig() {
  const defaults = {
    checkIntervalMs: 300000,
    passCount: 5,
    targetMetric: 1,
    maxMutations: 50,
    mutationCooldownMs: 10000,
    commandTimeoutMs: 120000,
    rollbackOnRegression: true,
    minImprovementEpsilon: 0.001,
    measurement: {
      command: "<measurement_tool_command>",
      args: ["<measurement_tool_arg_1>"],
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
    logLevel: "info",
  };

  let fileConfig = {};
  if (fs.existsSync(CONFIG_PATH)) {
    try {
      fileConfig = JSON.parse(fs.readFileSync(CONFIG_PATH, "utf-8"));
    } catch (error) {
      log("warn", "eval_config_parse_error", { error: error.message });
    }
  }

  const cfg = {
    ...defaults,
    ...fileConfig,
    measurement: { ...defaults.measurement, ...(fileConfig.measurement || {}) },
    evaluator: { ...defaults.evaluator, ...(fileConfig.evaluator || {}) },
    mutator: { ...defaults.mutator, ...(fileConfig.mutator || {}) },
  };

  currentLogLevel = cfg.logLevel;
  return cfg;
}

function validateConfig(config) {
  const errors = [];

  if (hasPlaceholder(config.measurement.command)) {
    errors.push("measurement.command contains placeholder");
  }
  if (hasPlaceholder(config.targetFilePath)) {
    errors.push("targetFilePath contains placeholder");
  }
  if (!Array.isArray(config.measurement.args)) {
    errors.push("measurement.args must be an array");
  }
  if (!Number.isFinite(config.passCount) || config.passCount <= 0) {
    errors.push("passCount must be > 0");
  }
  if (!Number.isFinite(config.targetMetric) || config.targetMetric < 0 || config.targetMetric > 1) {
    errors.push("targetMetric must be between 0 and 1");
  }
  if (!Number.isFinite(config.commandTimeoutMs) || config.commandTimeoutMs <= 0) {
    errors.push("commandTimeoutMs must be > 0");
  }
  if (!Number.isFinite(config.minImprovementEpsilon) || config.minImprovementEpsilon < 0) {
    errors.push("minImprovementEpsilon must be >= 0");
  }
  if (!config.targetFilePath || typeof config.targetFilePath !== "string") {
    errors.push("targetFilePath must be a non-empty string");
  } else {
    const absoluteTarget = path.resolve(ROOT_DIR, config.targetFilePath);
    if (!fs.existsSync(absoluteTarget)) {
      errors.push("targetFilePath does not exist");
    }
  }

  return errors;
}

function acquireLock() {
  try {
    const fd = fs.openSync(LOCK_PATH, "wx");
    fs.writeFileSync(
      fd,
      JSON.stringify({ pid: process.pid, timestamp: new Date().toISOString() })
    );
    fs.closeSync(fd);
    return true;
  } catch (error) {
    if (error.code !== "EEXIST") {
      log("error", "lock_acquire_failed", { error: error.message });
    }
    return false;
  }
}

function releaseLock() {
  try {
    if (fs.existsSync(LOCK_PATH)) {
      fs.unlinkSync(LOCK_PATH);
    }
  } catch (error) {
    log("warn", "lock_release_failed", { error: error.message });
  }
}

function readState() {
  if (!fs.existsSync(STATE_PATH)) {
    return { cycles: 0, mutations: 0, lastPassRate: 0, status: "idle" };
  }

  try {
    return JSON.parse(fs.readFileSync(STATE_PATH, "utf-8"));
  } catch {
    return { cycles: 0, mutations: 0, lastPassRate: 0, status: "idle" };
  }
}

function writeState(state) {
  fs.writeFileSync(STATE_TMP_PATH, JSON.stringify(state, null, 2), "utf-8");
  fs.renameSync(STATE_TMP_PATH, STATE_PATH);
}

function resolveCwd(cwd) {
  if (!cwd) {
    return ROOT_DIR;
  }
  return path.isAbsolute(cwd) ? cwd : path.resolve(ROOT_DIR, cwd);
}

function runCommand(command, args, options = {}) {
  if (hasPlaceholder(command)) {
    throw new Error("Command contains placeholder");
  }
  const safeArgs = Array.isArray(args) ? args.map((item) => String(item)) : [];
  return execFileSync(command, safeArgs, {
    cwd: options.cwd || ROOT_DIR,
    env: process.env,
    encoding: "utf-8",
    maxBuffer: 10 * 1024 * 1024,
    timeout: options.timeoutMs,
    input: options.input,
    stdio: ["ignore", "pipe", "pipe"],
  });
}

function executeMeasurementPass(config, runId) {
  const output = runCommand(config.measurement.command, config.measurement.args, {
    cwd: resolveCwd(config.measurement.cwd),
    timeoutMs: config.commandTimeoutMs,
  });

  return {
    runId,
    output,
    measuredAt: new Date().toISOString(),
  };
}

function normalizeBinaryValue(rawText) {
  const text = String(rawText || "").trim().toLowerCase();
  if (text === "1" || text === "pass" || text === "true") {
    return 1;
  }
  if (text === "0" || text === "fail" || text === "false") {
    return 0;
  }
  try {
    const parsed = JSON.parse(text);
    if (parsed && (parsed.pass === 1 || parsed.pass === 0)) {
      return parsed.pass;
    }
  } catch (_) {
    // Fallback heuristics below.
  }
  return /\bpass\b/.test(text) ? 1 : 0;
}

function evaluatePass(config, measurement) {
  if (hasPlaceholder(config.evaluator.command)) {
    return {
      pass: normalizeBinaryValue(measurement.output),
      evidence: "fallback parser",
      evaluatorMode: "local_fallback",
    };
  }

  const evalOutput = runCommand(config.evaluator.command, config.evaluator.args, {
    cwd: ROOT_DIR,
    timeoutMs: config.commandTimeoutMs,
    input: measurement.output,
  });

  return {
    pass: normalizeBinaryValue(evalOutput),
    evidence: String(evalOutput).trim().slice(0, 240),
    evaluatorMode: "command",
  };
}

function median(values) {
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  if (sorted.length % 2 === 0) {
    return (sorted[mid - 1] + sorted[mid]) / 2;
  }
  return sorted[mid];
}

function mode(values) {
  const counts = new Map();
  for (const value of values) {
    counts.set(value, (counts.get(value) || 0) + 1);
  }

  let topValue = values[0] || 0;
  let topCount = -1;
  for (const [value, count] of counts.entries()) {
    if (count > topCount) {
      topValue = value;
      topCount = count;
    }
  }
  return topValue;
}

function aggregateScores(scores) {
  const passRate = scores.reduce((sum, current) => sum + current, 0) / scores.length;
  return {
    passRate,
    median: median(scores),
    mode: mode(scores),
    confidenceDelta: 1 / Math.sqrt(scores.length),
  };
}

function appendMutationLog(cycle, hypothesis, scoreBefore, scoreAfter, status) {
  const line = `[${String(cycle).padStart(3, "0")}] ${hypothesis} | ${scoreBefore.toFixed(4)} -> ${scoreAfter.toFixed(4)} | ${status}`;
  fs.appendFileSync(MUTATION_LOG_PATH, line + "\n", "utf-8");
}

function readTargetFile(targetFilePath) {
  return fs.readFileSync(path.resolve(ROOT_DIR, targetFilePath), "utf-8");
}

function writeTargetFile(targetFilePath, content) {
  const absolute = path.resolve(ROOT_DIR, targetFilePath);
  const tempPath = `${absolute}.tmp`;
  fs.writeFileSync(tempPath, content, "utf-8");
  fs.renameSync(tempPath, absolute);
}

function backupTargetFile(targetFilePath) {
  const absolute = path.resolve(ROOT_DIR, targetFilePath);
  const backupPath = `${absolute}.bak.${Date.now()}`;
  fs.copyFileSync(absolute, backupPath);
  return backupPath;
}

function restoreTargetFromBackup(backupPath, targetFilePath) {
  const absoluteTarget = path.resolve(ROOT_DIR, targetFilePath);
  if (!fs.existsSync(backupPath)) {
    return false;
  }
  fs.copyFileSync(backupPath, absoluteTarget);
  return true;
}

function removeBackupFile(backupPath) {
  if (!backupPath) {
    return;
  }
  try {
    if (fs.existsSync(backupPath)) {
      fs.unlinkSync(backupPath);
    }
  } catch (_) {
    // Backup cleanup failure should never fail the loop.
  }
}

function parseMutatorOutput(raw, fallbackContent, fallbackHypothesis) {
  const text = String(raw || "").trim();
  if (!text) {
    return {
      hypothesis: fallbackHypothesis,
      content: fallbackContent,
      mode: "empty_output_noop",
    };
  }

  try {
    const parsed = JSON.parse(text);
    if (parsed && typeof parsed.content === "string") {
      return {
        hypothesis:
          typeof parsed.hypothesis === "string" && parsed.hypothesis.trim()
            ? parsed.hypothesis.trim()
            : fallbackHypothesis,
        content: parsed.content,
        mode: "command_json",
      };
    }
  } catch (_) {
    // Raw text mode below.
  }

  return {
    hypothesis: fallbackHypothesis,
    content: text,
    mode: "command_raw",
  };
}

function mutateTarget(config, context) {
  const hypothesis = `Mutation for cycle ${context.cycle}: improve objective alignment`;
  appendMutationLog(
    context.cycle,
    hypothesis,
    context.previousPassRate,
    context.currentPassRate,
    "planned"
  );

  if (hasPlaceholder(config.mutator.command)) {
    return {
      hypothesis,
      content: context.currentContent,
      mode: "placeholder_noop",
    };
  }

  const mutatorOutput = runCommand(config.mutator.command, config.mutator.args, {
    cwd: ROOT_DIR,
    timeoutMs: config.commandTimeoutMs,
    input: JSON.stringify(
      {
        cycle: context.cycle,
        previousPassRate: context.previousPassRate,
        currentPassRate: context.currentPassRate,
        scores: context.scores,
        targetMetric: context.targetMetric,
        targetFilePath: config.targetFilePath,
        content: context.currentContent,
      },
      null,
      2
    ),
  });

  return parseMutatorOutput(mutatorOutput, context.currentContent, hypothesis);
}

function shouldMutate(aggregate, config) {
  return aggregate.passRate + aggregate.confidenceDelta < config.targetMetric;
}

async function executeEvalCycle(config, state) {
  currentLogLevel = config.logLevel || currentLogLevel;
  const cycleId = randomUUID();
  const cycleNumber = state.cycles + 1;
  const measurements = [];
  const evaluations = [];

  log("info", "eval_cycle_start", {
    cycleId,
    cycleNumber,
    passCount: config.passCount,
    targetMetric: config.targetMetric,
  });

  for (let idx = 0; idx < config.passCount; idx += 1) {
    const measurement = executeMeasurementPass(config, `${cycleNumber}-${idx + 1}`);
    const evaluation = evaluatePass(config, measurement);
    measurements.push(measurement);
    evaluations.push(evaluation);
  }

  const scores = evaluations.map((item) => item.pass);
  const aggregate = aggregateScores(scores);
  const targetContent = readTargetFile(config.targetFilePath);
  let pendingRollback = state.pendingRollback || null;
  let rolledBack = false;

  if (
    config.rollbackOnRegression &&
    pendingRollback &&
    Number.isFinite(pendingRollback.baselinePassRate)
  ) {
    const baseline = pendingRollback.baselinePassRate;
    const epsilon = config.minImprovementEpsilon || 0;
    if (aggregate.passRate + epsilon < baseline) {
      if (restoreTargetFromBackup(pendingRollback.backupPath, config.targetFilePath)) {
        rolledBack = true;
        appendMutationLog(
          cycleNumber,
          "auto_rollback_on_regression",
          baseline,
          aggregate.passRate,
          "rolled_back"
        );
        log("warn", "mutation_rolled_back", {
          cycleId,
          cycleNumber,
          backupPath: pendingRollback.backupPath,
          baselinePassRate: baseline,
          currentPassRate: aggregate.passRate,
        });
      }
      removeBackupFile(pendingRollback.backupPath);
      pendingRollback = null;
    } else if (aggregate.passRate >= baseline + epsilon) {
      removeBackupFile(pendingRollback.backupPath);
      pendingRollback = null;
    }
  }

  let status = "target_met";
  let mutated = false;
  if (shouldMutate(aggregate, config) && state.mutations < config.maxMutations) {
    const backupPath = backupTargetFile(config.targetFilePath);
    const mutation = mutateTarget(config, {
      cycle: cycleNumber,
      previousPassRate: state.lastPassRate || 0,
      currentPassRate: aggregate.passRate,
      scores,
      targetMetric: config.targetMetric,
      currentContent: targetContent,
    });
    writeTargetFile(config.targetFilePath, mutation.content);
    mutated = true;
    status = "mutation_triggered";
    pendingRollback = {
      backupPath,
      baselinePassRate: aggregate.passRate,
      cycleNumber,
    };

    appendMutationLog(
      cycleNumber,
      mutation.hypothesis,
      state.lastPassRate || 0,
      aggregate.passRate,
      "applied"
    );

    log("info", "mutation_applied", {
      cycleId,
      cycleNumber,
      backupPath,
      mutationMode: mutation.mode,
      hypothesis: mutation.hypothesis,
      targetFilePath: config.targetFilePath,
    });
  } else if (state.mutations >= config.maxMutations) {
    status = "max_mutations_reached";
  }

  log("info", "eval_cycle_complete", {
    cycleId,
    cycleNumber,
    scores,
    passRate: aggregate.passRate,
    median: aggregate.median,
    mode: aggregate.mode,
    confidenceDelta: aggregate.confidenceDelta,
    targetMetric: config.targetMetric,
    rolledBack,
    status,
  });

  return {
    status,
    mutated,
    rolledBack,
    pendingRollback,
    aggregate,
    scores,
    cycleNumber,
  };
}

async function runOnce(options = {}) {
  ensureMemoryFiles();
  const config = loadConfig();
  if (options.dryRun) {
    const validationErrors = validateConfig(config);
    return {
      status: "dry_run",
      config,
      validationErrors,
    };
  }

  const validationErrors = validateConfig(config);
  if (validationErrors.length > 0) {
    return {
      status: "invalid_config",
      errors: validationErrors,
    };
  }

  if (!acquireLock()) {
    return { status: "locked" };
  }

  try {
    const state = readState();
    const cycleResult = await executeEvalCycle(config, state);
    const nextState = {
      cycles: cycleResult.cycleNumber,
      mutations: state.mutations + (cycleResult.mutated ? 1 : 0),
      lastPassRate: cycleResult.aggregate.passRate,
      status: cycleResult.status,
      pendingRollback: cycleResult.pendingRollback,
      updatedAt: new Date().toISOString(),
    };
    writeState(nextState);

    return {
      status: cycleResult.status,
      state: nextState,
      aggregate: cycleResult.aggregate,
      scores: cycleResult.scores,
    };
  } finally {
    releaseLock();
  }
}

async function runLoop() {
  ensureMemoryFiles();
  const config = loadConfig();
  const validationErrors = validateConfig(config);

  if (validationErrors.length > 0) {
    log("error", "eval_config_invalid", { errors: validationErrors });
    return { status: "invalid_config", errors: validationErrors };
  }

  if (!acquireLock()) {
    log("warn", "eval_motor_locked");
    return { status: "locked" };
  }

  try {
    let state = readState();
    while (state.mutations < config.maxMutations) {
      const cycleResult = await executeEvalCycle(config, state);
      state = {
        cycles: cycleResult.cycleNumber,
        mutations: state.mutations + (cycleResult.mutated ? 1 : 0),
        lastPassRate: cycleResult.aggregate.passRate,
        status: cycleResult.status,
        pendingRollback: cycleResult.pendingRollback,
        updatedAt: new Date().toISOString(),
      };
      writeState(state);

      if (cycleResult.aggregate.passRate >= config.targetMetric) {
        return { status: "target_met", state };
      }

      if (!cycleResult.mutated) {
        return { status: "stalled", state };
      }

      if (config.mutationCooldownMs > 0) {
        await new Promise((resolve) => setTimeout(resolve, config.mutationCooldownMs));
      }
    }

    return { status: "max_mutations_reached", state };
  } finally {
    releaseLock();
  }
}

if (require.main === module) {
  const args = new Set(process.argv.slice(2));
  const dryRun = args.has("--dry-run");
  const once = args.has("--once") || dryRun;

  const runner = once ? runOnce({ dryRun }) : runLoop();
  runner
    .then((result) => {
      process.stdout.write(JSON.stringify(result, null, 2) + "\n");
      process.exitCode = result.status === "invalid_config" ? 1 : 0;
    })
    .catch((error) => {
      process.stderr.write(`${error.stack || error.message}\n`);
      process.exitCode = 1;
    });
}

module.exports = {
  loadConfig,
  validateConfig,
  normalizeBinaryValue,
  aggregateScores,
  shouldMutate,
  parseMutatorOutput,
  restoreTargetFromBackup,
  runOnce,
  runLoop,
  executeEvalCycle,
};
