/**
 * MCP Server — Gemini Content Analyzer for TakiOS Curriculum Research
 *
 * Minimal JSON-RPC 2.0 over stdio implementation of the Model Context Protocol.
 * Exposes three tools for analyzing web content via Google Gemini API and
 * extracting structured curriculum data (bilingual de/en).
 *
 * Compliance:
 *   - ISO/IEC 42001: structured traceability logging per tool invocation
 *   - EU AI Act Art. 12: timestamp, request_id, model, token estimates logged
 *   - BSI TR-03161: no shell execution, no hardcoded secrets
 *
 * Security:
 *   - CommonJS format (.cjs) per workspace convention
 *   - Node.js built-ins only (readline, https, crypto, fs, path)
 *   - API key exclusively from environment variable
 *
 * @module mcp-gemini
 */

"use strict";

const readline = require("node:readline");
const https = require("node:https");
const fs = require("node:fs");
const path = require("node:path");
const { randomUUID, createHash } = require("node:crypto");

// ─── Constants ───────────────────────────────────────────────────────────────

const ROOT_DIR = path.resolve(__dirname, "..", "..");
const CONFIG_PATH = path.join(ROOT_DIR, "config", "mcp-gemini.json");
const LOG_PATH = path.join(ROOT_DIR, "memory", "mcp-gemini.log");

const PROTOCOL_VERSION = "2024-11-05";
const SERVER_NAME = "gemini-analyzer";
const SERVER_VERSION = "1.0.0";

const LOG_LEVELS = { debug: 0, info: 1, warn: 2, error: 3 };

// ─── Configuration ───────────────────────────────────────────────────────────

function loadConfig() {
  const defaults = {
    model: "gemini-2.0-flash",
    baseUrl: "https://generativelanguage.googleapis.com/v1beta",
    temperature: 0.3,
    maxOutputTokens: 4096,
    requestTimeoutMs: 30000,
    maxRetries: 3,
    retryBaseDelayMs: 1000,
    maxContentChars: 100000,
    logLevel: "info",
  };

  let fileConfig = {};
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      fileConfig = JSON.parse(fs.readFileSync(CONFIG_PATH, "utf-8"));
    }
  } catch (_) {
    // Fall through to defaults.
  }

  return { ...defaults, ...fileConfig };
}

const config = loadConfig();
let currentLogLevel = config.logLevel || "info";

// ─── Logging (stderr only — stdout reserved for JSON-RPC) ───────────────────

function log(level, message, meta = {}) {
  if (LOG_LEVELS[level] < LOG_LEVELS[currentLogLevel]) return;

  const entry = {
    timestamp: new Date().toISOString(),
    level,
    component: "mcp-gemini.cjs",
    message,
    ...meta,
  };
  const line = JSON.stringify(entry);

  // MCP servers MUST only write JSON-RPC on stdout; diagnostics go to stderr.
  process.stderr.write(line + "\n");

  try {
    fs.mkdirSync(path.dirname(LOG_PATH), { recursive: true });
    fs.appendFileSync(LOG_PATH, line + "\n", "utf-8");
  } catch (_) {
    // Logging must never crash the server.
  }
}

// ─── Content Hashing (duplicate detection) ───────────────────────────────────

const _seenHashes = new Set();

function contentHash(text) {
  return createHash("sha256").update(text).digest("hex").slice(0, 16);
}

function isDuplicate(text) {
  const hash = contentHash(text);
  if (_seenHashes.has(hash)) return true;
  _seenHashes.add(hash);
  return false;
}

// ─── Gemini API Client ──────────────────────────────────────────────────────

function getApiKey() {
  const key = process.env.GEMINI_API_KEY;
  if (!key || key.trim() === "") {
    return null;
  }
  return key.trim();
}

/**
 * Call Gemini generateContent endpoint.
 * @param {string} prompt - The prompt to send
 * @param {string} requestId - UUID for traceability
 * @returns {Promise<{text: string, tokenEstimate: {input: number, output: number}}>}
 */
function callGemini(prompt, requestId) {
  const apiKey = getApiKey();
  if (!apiKey) {
    return Promise.reject(new Error(
      "GEMINI_API_KEY environment variable is not set. " +
      "Please configure it in .vscode/mcp.json or your environment."
    ));
  }

  const url = new URL(
    `${config.baseUrl}/models/${config.model}:generateContent?key=${apiKey}`
  );

  const body = JSON.stringify({
    contents: [{ parts: [{ text: prompt }] }],
    generationConfig: {
      temperature: config.temperature,
      maxOutputTokens: config.maxOutputTokens,
    },
  });

  const inputTokenEstimate = Math.ceil(prompt.length / 4);

  return retryWithBackoff(() => {
    return new Promise((resolve, reject) => {
      const reqOptions = {
        hostname: url.hostname,
        port: 443,
        path: url.pathname + url.search,
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Content-Length": Buffer.byteLength(body),
        },
        timeout: config.requestTimeoutMs,
      };

      const req = https.request(reqOptions, (res) => {
        let data = "";
        res.on("data", (chunk) => { data += chunk; });
        res.on("end", () => {
          if (res.statusCode === 429) {
            reject(Object.assign(new Error("Rate limited by Gemini API"), { retryable: true, statusCode: 429 }));
            return;
          }
          if (res.statusCode === 503) {
            reject(Object.assign(new Error("Gemini API temporarily unavailable"), { retryable: true, statusCode: 503 }));
            return;
          }
          if (res.statusCode < 200 || res.statusCode >= 300) {
            let detail = data;
            try { detail = JSON.parse(data).error?.message || data; } catch (_) { /* use raw */ }
            reject(Object.assign(new Error(`Gemini API error (${res.statusCode}): ${detail}`), { statusCode: res.statusCode }));
            return;
          }

          try {
            const parsed = JSON.parse(data);
            const text = parsed.candidates?.[0]?.content?.parts?.[0]?.text || "";
            const outputTokenEstimate = Math.ceil(text.length / 4);

            log("info", "gemini_call_complete", {
              request_id: requestId,
              model: config.model,
              input_token_estimate: inputTokenEstimate,
              output_token_estimate: outputTokenEstimate,
            });

            resolve({ text, tokenEstimate: { input: inputTokenEstimate, output: outputTokenEstimate } });
          } catch (err) {
            reject(new Error(`Failed to parse Gemini response: ${err.message}`));
          }
        });
      });

      req.on("timeout", () => {
        req.destroy();
        reject(Object.assign(new Error("Gemini API request timed out"), { retryable: true }));
      });

      req.on("error", (err) => {
        reject(Object.assign(new Error(`Network error: ${err.message}`), { retryable: true }));
      });

      req.write(body);
      req.end();
    });
  }, config.maxRetries, config.retryBaseDelayMs, requestId);
}

/**
 * Retry a function with exponential backoff.
 */
function retryWithBackoff(fn, maxRetries, baseDelayMs, requestId) {
  let attempt = 0;

  function tryOnce() {
    return fn().catch((err) => {
      attempt++;
      if (!err.retryable || attempt >= maxRetries) {
        throw err;
      }
      const delay = baseDelayMs * Math.pow(2, attempt - 1);
      log("warn", "gemini_retry", { request_id: requestId, attempt, delay_ms: delay, error: err.message });
      return new Promise((resolve) => setTimeout(resolve, delay)).then(tryOnce);
    });
  }

  return tryOnce();
}

// ─── Content Chunking ────────────────────────────────────────────────────────

function chunkContent(text, maxChars) {
  if (text.length <= maxChars) return [text];

  const chunks = [];
  let start = 0;
  while (start < text.length) {
    let end = start + maxChars;
    // Try to break at paragraph or sentence boundary.
    if (end < text.length) {
      const lastParagraph = text.lastIndexOf("\n\n", end);
      if (lastParagraph > start + maxChars * 0.5) {
        end = lastParagraph;
      } else {
        const lastSentence = text.lastIndexOf(". ", end);
        if (lastSentence > start + maxChars * 0.5) {
          end = lastSentence + 1;
        }
      }
    }
    chunks.push(text.slice(start, end));
    start = end;
  }
  return chunks;
}

// ─── Tool Implementations ────────────────────────────────────────────────────

/**
 * Analyze page content: topic, relevance to education, difficulty level.
 */
async function analyzePageContent(params) {
  const { content, url } = params;

  if (!content || typeof content !== "string" || content.trim() === "") {
    return { error: "Parameter 'content' is required and must be non-empty text." };
  }

  if (isDuplicate(content)) {
    return {
      duplicate: true,
      message: "This content has already been analyzed in this session.",
      content_hash: contentHash(content),
    };
  }

  const requestId = randomUUID();
  const chunks = chunkContent(content, config.maxContentChars);

  const prompt = `You are an expert educational content analyst for a medical technology (Medizintechnik) university curriculum.

Analyze the following web page content and return a JSON object with exactly these fields:
- "topic_de": Main topic in German (string)
- "topic_en": Main topic in English (string)
- "relevance_score": How relevant this is for studying medical technology at university level (0.0 to 1.0)
- "difficulty_level": One of "beginner", "intermediate", "advanced"
- "content_type": One of "lecture_material", "tutorial", "reference", "exercise", "research_paper", "documentation", "other"
- "key_concepts": Array of up to 10 key technical concepts found (strings)
- "suitable_modules": Array of module codes this could be relevant for (e.g., ["MT-M1", "MT-P1"]) based on these subjects: MATH, PHYS, ET, INF, MED, NAWI, ING, MESS, REG, MGMT, PRAXIS
- "quality_indicators": {"has_formulas": bool, "has_diagrams_mentioned": bool, "has_references": bool, "is_peer_reviewed": bool}
- "summary_de": Brief summary in German (max 200 chars)
- "summary_en": Brief summary in English (max 200 chars)

Respond ONLY with valid JSON, no markdown fencing.

${url ? `Source URL: ${url}\n` : ""}
Content (chunk 1 of ${chunks.length}):
${chunks[0]}`;

  const result = await callGemini(prompt, requestId);

  try {
    const parsed = JSON.parse(result.text);
    return { ...parsed, request_id: requestId, token_estimate: result.tokenEstimate };
  } catch (_) {
    return {
      raw_analysis: result.text,
      request_id: requestId,
      token_estimate: result.tokenEstimate,
      parse_warning: "Response was not valid JSON. Raw text returned.",
    };
  }
}

/**
 * Extract structured curriculum data from analyzed content.
 */
async function extractCurriculumData(params) {
  const { content, analysis, url } = params;

  if (!content || typeof content !== "string" || content.trim() === "") {
    return { error: "Parameter 'content' is required and must be non-empty text." };
  }

  const requestId = randomUUID();
  const chunks = chunkContent(content, config.maxContentChars);

  const analysisContext = analysis
    ? `\nPrevious analysis: ${JSON.stringify(analysis)}\n`
    : "";

  const prompt = `You are a curriculum data extractor for a German medical technology (Medizintechnik) university program.

Extract structured learning content from the following web page. Return a JSON object with exactly these fields:
- "title_de": Title in German (string)
- "title_en": Title in English (string)
- "body_de": Main educational content in German, formatted as Markdown with LaTeX math where applicable (string)
- "body_en": Main educational content in English, formatted as Markdown with LaTeX math where applicable (string)
- "learning_objectives": Array of specific learning objectives (strings, in German)
- "references": Array of source references with URLs where available (strings)
- "keywords_de": Array of German keywords for indexing
- "keywords_en": Array of English keywords for indexing
- "prerequisite_knowledge": Array of assumed prior knowledge topics
- "estimated_study_time_minutes": Estimated time to study this content (integer)

Keep body content educational and factual. Include mathematical formulas in LaTeX notation ($$...$$) where applicable.
Respond ONLY with valid JSON, no markdown fencing.
${analysisContext}
${url ? `Source URL: ${url}\n` : ""}
Content (chunk 1 of ${chunks.length}):
${chunks[0]}`;

  const result = await callGemini(prompt, requestId);

  try {
    const parsed = JSON.parse(result.text);
    return { ...parsed, request_id: requestId, token_estimate: result.tokenEstimate, source_url: url || null };
  } catch (_) {
    return {
      raw_extraction: result.text,
      request_id: requestId,
      token_estimate: result.tokenEstimate,
      parse_warning: "Response was not valid JSON. Raw text returned.",
    };
  }
}

/**
 * Summarize content specifically for a given module.
 */
async function summarizeForModule(params) {
  const { content, module_code, module_name, module_units } = params;

  if (!content || typeof content !== "string" || content.trim() === "") {
    return { error: "Parameter 'content' is required and must be non-empty text." };
  }
  if (!module_code || typeof module_code !== "string") {
    return { error: "Parameter 'module_code' is required (e.g., 'MT-M1')." };
  }

  const requestId = randomUUID();
  const chunks = chunkContent(content, config.maxContentChars);

  const moduleContext = module_name ? `Module: ${module_code} — ${module_name}` : `Module: ${module_code}`;
  const unitsContext = module_units && Array.isArray(module_units)
    ? `\nLearning units in this module:\n${module_units.map((u, i) => `  ${i + 1}. ${u}`).join("\n")}`
    : "";

  const prompt = `You are a study material curator for a German medical technology university program.

Given the following web content, create a module-specific summary for "${moduleContext}".
${unitsContext}

Return a JSON object with exactly these fields:
- "module_code": "${module_code}"
- "relevance_score": How relevant this content is for this specific module (0.0 to 1.0)
- "summary_de": Concise summary in German focused on module-relevant aspects (string, max 500 chars)
- "summary_en": Concise summary in English focused on module-relevant aspects (string, max 500 chars)
- "covered_units": Array of unit names/topics from the module that this content covers
- "key_formulas": Array of key mathematical formulas in LaTeX notation relevant to this module
- "recommended_reading_order": Integer 1-10 indicating when to read this (1=first, during prerequisites, 10=last, for advanced review)
- "difficulty_match": One of "too_easy", "appropriate", "too_advanced" for this module's typical semester level

Respond ONLY with valid JSON, no markdown fencing.

Content (chunk 1 of ${chunks.length}):
${chunks[0]}`;

  const result = await callGemini(prompt, requestId);

  try {
    const parsed = JSON.parse(result.text);
    return { ...parsed, request_id: requestId, token_estimate: result.tokenEstimate };
  } catch (_) {
    return {
      raw_summary: result.text,
      request_id: requestId,
      token_estimate: result.tokenEstimate,
      parse_warning: "Response was not valid JSON. Raw text returned.",
    };
  }
}

// ─── Tool Registry ───────────────────────────────────────────────────────────

const TOOLS = [
  {
    name: "analyze_page_content",
    description:
      "Analyze web page content for educational relevance to the TakiOS medical technology curriculum. " +
      "Returns topic classification, relevance score, difficulty level, suitable modules, and quality indicators.",
    inputSchema: {
      type: "object",
      properties: {
        content: { type: "string", description: "The text content of the web page to analyze" },
        url: { type: "string", description: "Source URL of the page (optional, for reference)" },
      },
      required: ["content"],
    },
  },
  {
    name: "extract_curriculum_data",
    description:
      "Extract structured bilingual (de/en) curriculum data from web content. " +
      "Returns title, body, learning objectives, references, and keywords in the TakiOS content schema.",
    inputSchema: {
      type: "object",
      properties: {
        content: { type: "string", description: "The text content to extract curriculum data from" },
        analysis: {
          type: "object",
          description: "Optional: previous analysis result from analyze_page_content for context",
        },
        url: { type: "string", description: "Source URL (optional, stored as reference)" },
      },
      required: ["content"],
    },
  },
  {
    name: "summarize_for_module",
    description:
      "Summarize web content specifically for a given TakiOS curriculum module. " +
      "Returns module-specific relevance, covered units, key formulas, and difficulty assessment.",
    inputSchema: {
      type: "object",
      properties: {
        content: { type: "string", description: "The text content to summarize" },
        module_code: { type: "string", description: "Module code, e.g., 'MT-M1' for Mathematics 1" },
        module_name: { type: "string", description: "Optional: human-readable module name" },
        module_units: {
          type: "array",
          items: { type: "string" },
          description: "Optional: list of learning unit names within the module",
        },
      },
      required: ["content", "module_code"],
    },
  },
];

const TOOL_HANDLERS = {
  analyze_page_content: analyzePageContent,
  extract_curriculum_data: extractCurriculumData,
  summarize_for_module: summarizeForModule,
};

// ─── JSON-RPC / MCP Protocol Handling ────────────────────────────────────────

function makeResponse(id, result) {
  return JSON.stringify({ jsonrpc: "2.0", id, result });
}

function makeError(id, code, message, data) {
  const error = { code, message };
  if (data !== undefined) error.data = data;
  return JSON.stringify({ jsonrpc: "2.0", id, error });
}

// Standard JSON-RPC error codes
const ERR_PARSE = -32700;
const ERR_INVALID_REQUEST = -32600;
const ERR_METHOD_NOT_FOUND = -32601;
const ERR_INVALID_PARAMS = -32602;
const ERR_INTERNAL = -32603;

function handleInitialize(id, _params) {
  return makeResponse(id, {
    protocolVersion: PROTOCOL_VERSION,
    capabilities: {
      tools: {},
    },
    serverInfo: {
      name: SERVER_NAME,
      version: SERVER_VERSION,
    },
  });
}

function handleToolsList(id) {
  return makeResponse(id, { tools: TOOLS });
}

async function handleToolsCall(id, params) {
  const { name, arguments: args } = params || {};

  if (!name || typeof name !== "string") {
    return makeError(id, ERR_INVALID_PARAMS, "Missing or invalid 'name' in tools/call");
  }

  const handler = TOOL_HANDLERS[name];
  if (!handler) {
    return makeError(id, ERR_METHOD_NOT_FOUND, `Unknown tool: ${name}`);
  }

  try {
    const result = await handler(args || {});

    if (result.error) {
      return makeResponse(id, {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
        isError: true,
      });
    }

    return makeResponse(id, {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
    });
  } catch (err) {
    log("error", "tool_call_error", { tool: name, error: err.message });
    return makeResponse(id, {
      content: [{ type: "text", text: JSON.stringify({ error: err.message }) }],
      isError: true,
    });
  }
}

async function handleMessage(line) {
  let msg;
  try {
    msg = JSON.parse(line);
  } catch (_) {
    return makeError(null, ERR_PARSE, "Parse error: invalid JSON");
  }

  if (!msg.jsonrpc || msg.jsonrpc !== "2.0") {
    return makeError(msg.id || null, ERR_INVALID_REQUEST, "Invalid JSON-RPC: missing or wrong 'jsonrpc' field");
  }

  // Notifications (no id) — acknowledged silently.
  if (msg.id === undefined || msg.id === null) {
    if (msg.method === "notifications/initialized") {
      log("info", "client_initialized");
    }
    return null; // No response for notifications.
  }

  if (!msg.method || typeof msg.method !== "string") {
    return makeError(msg.id, ERR_INVALID_REQUEST, "Invalid JSON-RPC: missing 'method'");
  }

  switch (msg.method) {
    case "initialize":
      return handleInitialize(msg.id, msg.params);
    case "tools/list":
      return handleToolsList(msg.id);
    case "tools/call":
      return handleToolsCall(msg.id, msg.params);
    case "ping":
      return makeResponse(msg.id, {});
    default:
      return makeError(msg.id, ERR_METHOD_NOT_FOUND, `Method not found: ${msg.method}`);
  }
}

// ─── CLI: --help flag ────────────────────────────────────────────────────────

if (process.argv.includes("--help") || process.argv.includes("-h")) {
  process.stdout.write(
    `${SERVER_NAME} v${SERVER_VERSION}\n` +
    `MCP Server for Gemini-powered curriculum content analysis.\n\n` +
    `Usage: node ${path.basename(__filename)} [options]\n\n` +
    `The server communicates via JSON-RPC 2.0 over stdio.\n` +
    `Configure via config/mcp-gemini.json and GEMINI_API_KEY env variable.\n\n` +
    `Options:\n` +
    `  --help, -h    Show this help message\n\n` +
    `Tools provided:\n` +
    `  analyze_page_content     Analyze web content for educational relevance\n` +
    `  extract_curriculum_data  Extract bilingual curriculum data from content\n` +
    `  summarize_for_module     Summarize content for a specific module\n\n` +
    `Environment:\n` +
    `  GEMINI_API_KEY  Google Gemini API key (required)\n`
  );
  process.exit(0);
}

// ─── Main: stdio transport ───────────────────────────────────────────────────

function startServer() {
  log("info", "server_starting", { version: SERVER_VERSION, model: config.model });

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false,
  });

  // Disable default output on the readline interface —
  // we write JSON-RPC responses directly to stdout ourselves.
  rl.output = null;

  rl.on("line", async (line) => {
    if (!line.trim()) return;

    try {
      const response = await handleMessage(line);
      if (response !== null) {
        process.stdout.write(response + "\n");
      }
    } catch (err) {
      log("error", "unhandled_message_error", { error: err.message });
      const errResponse = makeError(null, ERR_INTERNAL, `Internal error: ${err.message}`);
      process.stdout.write(errResponse + "\n");
    }
  });

  rl.on("close", () => {
    log("info", "server_shutdown", { reason: "stdin_closed" });
    process.exit(0);
  });

  process.on("SIGTERM", () => {
    log("info", "server_shutdown", { reason: "SIGTERM" });
    rl.close();
    process.exit(0);
  });

  process.on("SIGINT", () => {
    log("info", "server_shutdown", { reason: "SIGINT" });
    rl.close();
    process.exit(0);
  });
}

// ─── Exports for testing ─────────────────────────────────────────────────────

module.exports = {
  handleMessage,
  loadConfig,
  chunkContent,
  contentHash,
  isDuplicate,
  analyzePageContent,
  extractCurriculumData,
  summarizeForModule,
  TOOLS,
  TOOL_HANDLERS,
  _resetDuplicates: () => _seenHashes.clear(),
  _getSeenHashes: () => _seenHashes,
};

// Start server only when run directly (not required as module).
if (require.main === module) {
  startServer();
}
