/**
 * AutoDream Execution Motor — File-Only Memory Consolidation
 *
 * This motor is intentionally isolated from the main codebase:
 * it ONLY reads/writes files inside memory/ to minimize integration
 * risk and reduce cross-layer coupling (ISO/IEC 42001 transparency).
 *
 * Compliance:
 *   - ISO/IEC 42001: explicit risk boundaries and deterministic behavior
 *   - EU AI Act Art. 12: structured traceability logs per cycle
 *   - BSI TR-03161: no shell execution, no hardcoded secrets
 *
 * Security:
 *   - CommonJS format (.cjs)
 *   - Node.js built-ins only
 *   - No execSync/shell=true, no network calls
 *
 * @module motor
 */

"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { randomUUID } = require("node:crypto");

// ─── Constants and Paths (memory/ only) ──────────────────────────────────────

// Optional override for tests; runtime still only touches the resolved memory dir.
const MEMORY_DIR = process.env.TAKIOS_MEMORY_DIR
  ? path.resolve(process.env.TAKIOS_MEMORY_DIR)
  : path.resolve(__dirname, "..", "..", "memory");

const CONTEXT_FILE = path.join(MEMORY_DIR, "context.mmd");
const CONTEXT_TMP = path.join(MEMORY_DIR, "context.mmd.tmp");
const ARCHIVE_DIR = path.join(MEMORY_DIR, "archive");
const INVALID_ARCHIVE_DIR = path.join(ARCHIVE_DIR, "invalid");
const LOG_FILE = path.join(MEMORY_DIR, "motor.log");
const STATE_FILE = path.join(MEMORY_DIR, "motor_state.json");
const LOCK_FILE = path.join(MEMORY_DIR, "motor.lock");
const CONFIG_FILE = path.join(MEMORY_DIR, "motor.json");

// ─── Configuration ───────────────────────────────────────────────────────────

/**
 * Load configuration from memory/motor.json or environment, with safe defaults.
 * Reading only memory/ keeps the motor isolated from the main codebase.
 * @returns {object} Motor configuration
 */
function loadConfig() {
  const defaults = {
    dreamIntervalMs: 12 * 60 * 60 * 1000, // 12 hours
    checkIntervalMs: 5 * 60 * 1000, // 5 minutes
    sessionThreshold: 50,
    maxIndexLines: 200,
    maxLineChars: 120,
    logLevel: "info", // debug | info | warn | error
  };

  const envOverrides = {
    dreamIntervalMs: process.env.TAKIOS_DREAM_INTERVAL_MS
      ? parseInt(process.env.TAKIOS_DREAM_INTERVAL_MS, 10)
      : undefined,
    checkIntervalMs: process.env.TAKIOS_CHECK_INTERVAL_MS
      ? parseInt(process.env.TAKIOS_CHECK_INTERVAL_MS, 10)
      : undefined,
    sessionThreshold: process.env.TAKIOS_SESSION_THRESHOLD
      ? parseInt(process.env.TAKIOS_SESSION_THRESHOLD, 10)
      : undefined,
    maxIndexLines: process.env.TAKIOS_MAX_INDEX_LINES
      ? parseInt(process.env.TAKIOS_MAX_INDEX_LINES, 10)
      : undefined,
    maxLineChars: process.env.TAKIOS_MAX_LINE_CHARS
      ? parseInt(process.env.TAKIOS_MAX_LINE_CHARS, 10)
      : undefined,
    logLevel: process.env.TAKIOS_LOG_LEVEL,
  };

  let fileConfig = {};
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      const raw = fs.readFileSync(CONFIG_FILE, "utf-8");
      fileConfig = JSON.parse(raw);
    }
  } catch (err) {
    log("warn", "config_read_error", { error: err.message });
  }

  const config = { ...defaults, ...fileConfig };
  for (const [key, value] of Object.entries(envOverrides)) {
    if (value !== undefined) config[key] = value;
  }
  return config;
}

// ─── Structured Logger (EU AI Act Art. 12) ───────────────────────────────────

const LOG_LEVELS = { debug: 0, info: 1, warn: 2, error: 3 };
let _logLevel = "info";

/**
 * Structured log output for traceability compliance.
 * Logs are append-only and scoped to memory/motor.log.
 * @param {"debug"|"info"|"warn"|"error"} level
 * @param {string} message
 * @param {object} [meta] Additional structured metadata
 */
function log(level, message, meta) {
  if (LOG_LEVELS[level] < LOG_LEVELS[_logLevel]) return;

  const entry = {
    timestamp: new Date().toISOString(),
    level,
    component: "motor.cjs",
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
    fs.appendFileSync(LOG_FILE, line + "\n");
  } catch (_) {
    // Logging must never terminate the motor.
  }
}

// ─── State and Lock Management ───────────────────────────────────────────────

function readState() {
  try {
    if (!fs.existsSync(STATE_FILE)) return {};
    return JSON.parse(fs.readFileSync(STATE_FILE, "utf-8"));
  } catch (err) {
    log("warn", "state_read_error", { error: err.message });
    return {};
  }
}

function writeState(state) {
  try {
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), "utf-8");
  } catch (err) {
    log("error", "state_write_error", { error: err.message });
  }
}

function acquireLock() {
  try {
    const fd = fs.openSync(LOCK_FILE, "wx");
    fs.writeFileSync(
      fd,
      JSON.stringify({ pid: process.pid, timestamp: new Date().toISOString() })
    );
    fs.closeSync(fd);
    return true;
  } catch (err) {
    if (err && err.code !== "EEXIST") {
      log("error", "lock_acquire_error", { error: err.message });
    }
    return false;
  }
}

function releaseLock() {
  try {
    if (fs.existsSync(LOCK_FILE)) fs.unlinkSync(LOCK_FILE);
  } catch (err) {
    log("warn", "lock_release_error", { error: err.message });
  }
}

// ─── Memory Index Management ─────────────────────────────────────────────────

function readMemoryIndex() {
  try {
    if (!fs.existsSync(CONTEXT_FILE)) return [];
    const content = fs.readFileSync(CONTEXT_FILE, "utf-8");
    return content
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.length > 0);
  } catch (err) {
    log("warn", "index_read_error", { error: err.message });
    return [];
  }
}

function writeMemoryIndex(lines, maxLines, maxChars) {
  try {
    const truncated = lines.slice(-maxLines);
    const formatted = truncated.map((line) => {
      const clean = line.replace(/\n/g, " ").trim();
      return clean.length <= maxChars
        ? clean
        : clean.substring(0, Math.max(0, maxChars - 3)) + "...";
    });
    fs.writeFileSync(CONTEXT_TMP, formatted.join("\n") + "\n", "utf-8");
    fs.renameSync(CONTEXT_TMP, CONTEXT_FILE);
  } catch (err) {
    log("error", "index_write_error", { error: err.message });
  }
}

// ─── Session Discovery and Parsing ───────────────────────────────────────────

const RESERVED_JSON_FILES = new Set(["motor.json", "motor_state.json"]);

function discoverSessionFiles() {
  try {
    if (!fs.existsSync(MEMORY_DIR)) return [];
    return fs
      .readdirSync(MEMORY_DIR, { withFileTypes: true })
      .filter((dirent) => dirent.isFile())
      .map((dirent) => dirent.name)
      .filter((name) => name.endsWith(".json"))
      .filter((name) => !RESERVED_JSON_FILES.has(name))
      .sort()
      .map((name) => path.join(MEMORY_DIR, name));
  } catch (err) {
    log("error", "session_discovery_error", { error: err.message });
    return [];
  }
}

function safeReadJson(filePath) {
  try {
    const raw = fs.readFileSync(filePath, "utf-8");
    return JSON.parse(raw);
  } catch (err) {
    log("warn", "session_json_invalid", { file: path.basename(filePath), error: err.message });
    return null;
  }
}

function normalizeCategory(category) {
  const safe = String(category || "").trim().toLowerCase();
  if (!safe) return "general";
  const allowed = new Set(["architecture", "decision", "error", "context", "general"]);
  return allowed.has(safe) ? safe : "general";
}

function loadSessionEntries(sessionFiles) {
  const entries = [];
  const processedFiles = [];
  const invalidFiles = [];

  for (const filePath of sessionFiles) {
    const payload = safeReadJson(filePath);
    if (!payload) {
      invalidFiles.push(filePath);
      continue;
    }

    const rawEntries = Array.isArray(payload)
      ? payload
      : Array.isArray(payload.entries)
      ? payload.entries
      : [];

    for (const entry of rawEntries) {
      if (!entry || typeof entry.content !== "string") continue;
      entries.push({
        content: entry.content,
        category: normalizeCategory(entry.category),
      });
    }

    processedFiles.push(filePath);
  }

  return { entries, processedFiles, invalidFiles };
}

// ─── Filler Detection ────────────────────────────────────────────────────────

const FILLER_PATTERNS = [
  /^(ok|okay|sure|got it|understood|alright|thanks|thank you)[.!,]?\s*$/i,
  /^(let me|i will|i'll|going to)\s+(check|look|see|try)/i,
  /^(here|this)\s+is\s+(the|a)\s+(result|output|answer)/i,
  /^status:\s*(in.progress|started|beginning)/i,
];

function isFiller(text) {
  const trimmed = text.trim();
  if (trimmed.length < 10) return true;
  return FILLER_PATTERNS.some((re) => re.test(trimmed));
}

// ─── Local Compaction Engine ─────────────────────────────────────────────────

function compactLocal(entries, existingIndex, maxLines, maxChars) {
  const result = [...existingIndex];
  const existingSet = new Set(existingIndex);

  const byCategory = {};
  for (const entry of entries) {
    const content = String(entry.content || "").replace(/\n/g, " ").trim();
    if (!content) continue;

    const category = normalizeCategory(entry.category);
    const isPreserved =
      category === "architecture" ||
      category === "decision" ||
      category === "error" ||
      category === "context";

    if (!isPreserved && isFiller(content)) continue;
    if (!byCategory[category]) byCategory[category] = [];
    byCategory[category].push(content);
  }

  const categories = Object.keys(byCategory).sort();
  for (const category of categories) {
    const unique = Array.from(new Set(byCategory[category]));
    const merged = unique.join("; ");
    if (!merged) continue;

    const prefix = `[${category}] `;
    const available = Math.max(0, maxChars - prefix.length);
    const body = merged.length <= available
      ? merged
      : merged.substring(0, Math.max(0, available - 3)) + "...";

    const line = prefix + body;
    if (!existingSet.has(line)) result.push(line);
  }

  return result.length > maxLines ? result.slice(-maxLines) : result;
}

// ─── Archiving ───────────────────────────────────────────────────────────────

function ensureDir(dirPath) {
  try {
    if (!fs.existsSync(dirPath)) fs.mkdirSync(dirPath, { recursive: true });
  } catch (err) {
    log("error", "directory_create_error", { path: dirPath, error: err.message });
  }
}

function archiveFiles(files, targetDir) {
  ensureDir(targetDir);
  for (const filePath of files) {
    try {
      const base = path.basename(filePath);
      let target = path.join(targetDir, base);
      if (fs.existsSync(target)) {
        const stamp = new Date().toISOString().replace(/[:.]/g, "-");
        target = path.join(targetDir, `${base}.${stamp}`);
      }
      fs.renameSync(filePath, target);
    } catch (err) {
      log("warn", "archive_error", { file: path.basename(filePath), error: err.message });
    }
  }
}

// ─── Trigger Logic ───────────────────────────────────────────────────────────

function shouldRunCycle(config, state, sessionCount, forceRun) {
  if (forceRun) return { run: true, trigger: "forced" };

  if (sessionCount >= config.sessionThreshold) {
    return { run: true, trigger: "threshold" };
  }

  const lastCycleAt = state.lastCycleAt ? Date.parse(state.lastCycleAt) : 0;
  if (!lastCycleAt || Date.now() - lastCycleAt >= config.dreamIntervalMs) {
    return { run: true, trigger: "interval" };
  }

  return { run: false, trigger: "idle" };
}

// ─── Dream Cycle Execution ───────────────────────────────────────────────────

function estimateTokens(text) {
  return Math.ceil(String(text || "").length / 4);
}

async function executeDreamCycle(trigger) {
  const config = loadConfig();
  _logLevel = config.logLevel || "info";

  ensureDir(MEMORY_DIR);

  if (!acquireLock()) {
    log("warn", "cycle_skipped_locked", { trigger });
    return { status: "locked" };
  }

  try {
    const cycleId = randomUUID();
    const startedAt = Date.now();

    log("info", "dream_cycle_start", {
      cycleId,
      trigger,
      method: "local_heuristic",
      resultCategory: "dream_cycle",
    });

    const state = readState();
    const sessionFiles = discoverSessionFiles();
    const sessionCount = sessionFiles.length;

    const { entries, processedFiles, invalidFiles } = loadSessionEntries(sessionFiles);
    const indexBefore = readMemoryIndex();
    const compacted = compactLocal(
      entries,
      indexBefore,
      config.maxIndexLines,
      config.maxLineChars
    );

    writeMemoryIndex(compacted, config.maxIndexLines, config.maxLineChars);
    archiveFiles(processedFiles, ARCHIVE_DIR);
    archiveFiles(invalidFiles, INVALID_ARCHIVE_DIR);

    const indexAfter = compacted.length;
    const durationMs = Date.now() - startedAt;

    const tokensBefore = estimateTokens(indexBefore.join("\n"));
    const tokensAfter = estimateTokens(compacted.join("\n"));
    const tokenDelta = tokensBefore - tokensAfter;

    const resultStatus = sessionCount === 0 ? "no_work" : "completed";
    const updatedState = {
      lastCycleId: cycleId,
      lastCycleAt: new Date().toISOString(),
      lastResult: resultStatus,
      lastSessionCount: sessionCount,
      lastEntryCount: entries.length,
      lastIndexLinesBefore: indexBefore.length,
      lastIndexLinesAfter: indexAfter,
    };
    writeState({ ...state, ...updatedState });

    log("info", "dream_cycle_complete", {
      cycleId,
      trigger,
      sessionsProcessed: sessionCount,
      entriesProcessed: entries.length,
      invalidSessions: invalidFiles.length,
      indexLinesBefore: indexBefore.length,
      indexLinesAfter: indexAfter,
      tokenDelta,
      durationMs,
      method: "local_heuristic",
      resultCategory: "dream_cycle",
      status: resultStatus,
    });

    return { status: resultStatus, cycleId };
  } finally {
    releaseLock();
  }
}

// ─── Scheduler ───────────────────────────────────────────────────────────────

function start() {
  const config = loadConfig();
  _logLevel = config.logLevel || "info";

  ensureDir(MEMORY_DIR);

  log("info", "motor_start", {
    config: {
      dreamIntervalMs: config.dreamIntervalMs,
      checkIntervalMs: config.checkIntervalMs,
      sessionThreshold: config.sessionThreshold,
      maxIndexLines: config.maxIndexLines,
      maxLineChars: config.maxLineChars,
      logLevel: config.logLevel,
    },
  });

  const runOnce = process.argv.includes("--run-once");
  const force = process.argv.includes("--force");

  const runIfNeeded = () => {
    try {
      const state = readState();
      const sessions = discoverSessionFiles();
      const decision = shouldRunCycle(config, state, sessions.length, force);
      if (decision.run) {
        executeDreamCycle(decision.trigger).catch((err) => {
          log("error", "cycle_error", { error: err.message });
          releaseLock();
        });
      }
    } catch (err) {
      log("error", "motor_loop_error", { error: err.message });
      releaseLock();
    }
  };

  if (runOnce) {
    runIfNeeded();
    return;
  }

  runIfNeeded();
  setInterval(runIfNeeded, config.checkIntervalMs);
}

// ─── CLI Support ─────────────────────────────────────────────────────────────

if (require.main === module) {
  start();
}

module.exports = {
  start,
  loadConfig,
  readMemoryIndex,
  writeMemoryIndex,
  compactLocal,
  discoverSessionFiles,
  loadSessionEntries,
  executeDreamCycle,
  shouldRunCycle,
};
