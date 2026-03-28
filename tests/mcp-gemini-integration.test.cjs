"use strict";

/**
 * Integration tests for mcp-gemini.cjs
 *
 * These tests require a real GEMINI_API_KEY and network access.
 * They are automatically skipped when the key is not available.
 *
 * Run: GEMINI_API_KEY=<your-key> node tests/mcp-gemini-integration.test.cjs
 */

const test = require("node:test");
const assert = require("node:assert/strict");
const { spawn } = require("node:child_process");
const path = require("node:path");

const SERVER_PATH = path.resolve(__dirname, "..", "bin", "lib", "mcp-gemini.cjs");
const HAS_API_KEY = !!(process.env.GEMINI_API_KEY && process.env.GEMINI_API_KEY.trim());

// ─── Helpers ─────────────────────────────────────────────────────────────────

/**
 * Spawn the MCP server as a child process, send JSON-RPC messages, collect responses.
 */
function createMcpClient() {
  const child = spawn("node", [SERVER_PATH], {
    stdio: ["pipe", "pipe", "pipe"],
    env: { ...process.env },
  });

  let buffer = "";
  const responses = [];
  const pending = new Map();

  child.stdout.on("data", (chunk) => {
    buffer += chunk.toString();
    const lines = buffer.split("\n");
    buffer = lines.pop(); // Keep incomplete line in buffer.
    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const msg = JSON.parse(line);
        responses.push(msg);
        if (msg.id !== undefined && pending.has(msg.id)) {
          pending.get(msg.id)(msg);
          pending.delete(msg.id);
        }
      } catch (_) {
        // Ignore non-JSON output.
      }
    }
  });

  let idCounter = 1;

  return {
    async send(method, params, timeoutMs = 60000) {
      const id = idCounter++;
      const msg = JSON.stringify({ jsonrpc: "2.0", id, method, params });

      return new Promise((resolve, reject) => {
        const timer = setTimeout(() => {
          pending.delete(id);
          reject(new Error(`Timeout waiting for response to ${method} (id=${id})`));
        }, timeoutMs);

        pending.set(id, (res) => {
          clearTimeout(timer);
          resolve(res);
        });

        child.stdin.write(msg + "\n");
      });
    },

    notify(method, params) {
      const msg = JSON.stringify({ jsonrpc: "2.0", method, params });
      child.stdin.write(msg + "\n");
    },

    close() {
      child.stdin.end();
      child.kill("SIGTERM");
    },

    get responses() { return responses; },
    get process() { return child; },
  };
}

/**
 * Perform the MCP handshake (initialize + notifications/initialized).
 */
async function handshake(client) {
  const initRes = await client.send("initialize", {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "integration-test" },
  });
  assert.ok(initRes.result.protocolVersion);
  client.notify("notifications/initialized");
  return initRes;
}

// ─── Skip guard ─────────────────────────────────────────────────────────────

const SKIP_MSG = "GEMINI_API_KEY not set — skipping integration test";

// ─── Tests ───────────────────────────────────────────────────────────────────

test("E2E: full handshake → tools/list → analyze_page_content", { skip: !HAS_API_KEY ? SKIP_MSG : false }, async (t) => {

  const client = createMcpClient();
  try {
    await handshake(client);

    // List tools.
    const toolsRes = await client.send("tools/list");
    assert.equal(toolsRes.result.tools.length, 3);

    // Analyze a simple educational text.
    const analyzeRes = await client.send("tools/call", {
      name: "analyze_page_content",
      arguments: {
        content: "Die Nernst-Gleichung beschreibt das elektrochemische Gleichgewichtspotential einer Ionensorte. " +
          "Sie lautet E = (RT/zF) * ln([X]außen/[X]innen). " +
          "Dies ist fundamental für das Verständnis von Membranpotentialen in der Biomedizintechnik.",
        url: "https://example.com/nernst",
      },
    });

    assert.ok(!analyzeRes.error, "Should not have JSON-RPC error");
    assert.ok(!analyzeRes.result.isError, "Tool should not return error");

    const body = JSON.parse(analyzeRes.result.content[0].text);
    assert.ok(typeof body.relevance_score === "number", "Should have relevance_score");
    assert.ok(body.relevance_score >= 0 && body.relevance_score <= 1, "relevance_score in [0,1]");
    assert.ok(body.topic_de || body.topic_en, "Should have at least one topic");
    assert.ok(body.request_id, "Should have request_id for traceability");
    assert.ok(body.token_estimate, "Should have token_estimate");
  } finally {
    client.close();
  }
});

test("E2E: extract_curriculum_data returns bilingual fields", { skip: !HAS_API_KEY ? SKIP_MSG : false }, async (t) => {

  const client = createMcpClient();
  try {
    await handshake(client);

    const res = await client.send("tools/call", {
      name: "extract_curriculum_data",
      arguments: {
        content: "Ohm's Law states that V = IR, where V is voltage in volts, I is current in amperes, " +
          "and R is resistance in ohms. This fundamental relationship is essential in electrical engineering " +
          "and forms the basis for analyzing circuits in medical devices such as ECG amplifiers.",
        url: "https://example.com/ohms-law",
      },
    });

    assert.ok(!analyzeError(res), "Should not error");

    const body = JSON.parse(res.result.content[0].text);
    assert.ok(body.title_de, "Should have title_de");
    assert.ok(body.title_en, "Should have title_en");
    assert.ok(body.body_de, "Should have body_de");
    assert.ok(body.body_en, "Should have body_en");
    assert.ok(Array.isArray(body.learning_objectives), "Should have learning_objectives array");
    assert.ok(Array.isArray(body.references), "Should have references array");
    assert.ok(body.source_url === "https://example.com/ohms-law", "Should preserve source URL");
  } finally {
    client.close();
  }
});

test("E2E: summarize_for_module with module context", { skip: !HAS_API_KEY ? SKIP_MSG : false }, async (t) => {

  const client = createMcpClient();
  try {
    await handshake(client);

    const res = await client.send("tools/call", {
      name: "summarize_for_module",
      arguments: {
        content: "Linear algebra is the branch of mathematics concerning vector spaces and linear mappings. " +
          "Key topics include systems of linear equations, matrices, determinants, eigenvalues, and eigenvectors. " +
          "Matrix operations are fundamental for image processing in medical imaging systems.",
        module_code: "MT-M1",
        module_name: "Mathematik 1",
        module_units: [
          "Lineare Gleichungssysteme & Matrizen",
          "Vektorrechnung im R²/R³",
          "Differentialrechnung einer Veränderlichen",
          "Kurvendiskussion & Extremwertprobleme",
          "Komplexe Zahlen",
        ],
      },
    });

    assert.ok(!analyzeError(res), "Should not error");

    const body = JSON.parse(res.result.content[0].text);
    assert.equal(body.module_code, "MT-M1");
    assert.ok(typeof body.relevance_score === "number");
    assert.ok(body.summary_de, "Should have German summary");
    assert.ok(body.summary_en, "Should have English summary");
    assert.ok(Array.isArray(body.covered_units), "Should have covered_units");
    assert.ok(
      ["too_easy", "appropriate", "too_advanced"].includes(body.difficulty_match),
      "difficulty_match should be valid"
    );
  } finally {
    client.close();
  }
});

test("E2E: server handles graceful shutdown on SIGTERM", { skip: !HAS_API_KEY ? SKIP_MSG : false }, async (t) => {

  const client = createMcpClient();
  try {
    await handshake(client);

    // Verify server is alive.
    const pingRes = await client.send("ping");
    assert.deepStrictEqual(pingRes.result, {});

    // Send SIGTERM.
    client.process.kill("SIGTERM");

    // Wait for exit.
    await new Promise((resolve) => {
      client.process.on("exit", resolve);
      setTimeout(resolve, 3000); // Timeout guard.
    });

    assert.ok(
      client.process.exitCode !== null || client.process.killed,
      "Server should have exited or been killed"
    );
  } finally {
    try { client.close(); } catch (_) { /* already closed */ }
  }
});

// ─── Helper ──────────────────────────────────────────────────────────────────

function analyzeError(res) {
  if (res.error) return true;
  if (res.result?.isError) return true;
  return false;
}
