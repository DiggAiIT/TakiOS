"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");
const { randomUUID } = require("node:crypto");

// ─── Load module under test ─────────────────────────────────────────────────

// Ensure no real API key leaks into unit tests.
const ORIGINAL_KEY = process.env.GEMINI_API_KEY;
delete process.env.GEMINI_API_KEY;

const mcp = require("../bin/lib/mcp-gemini.cjs");

// ─── Helpers ─────────────────────────────────────────────────────────────────

function jsonrpc(method, params, id) {
  return JSON.stringify({ jsonrpc: "2.0", id: id ?? 1, method, params });
}

async function send(method, params, id) {
  const raw = await mcp.handleMessage(jsonrpc(method, params, id));
  return raw ? JSON.parse(raw) : null;
}

// ─── 1. Protocol Handshake ──────────────────────────────────────────────────

test("initialize returns correct protocol version and capabilities", async () => {
  const res = await send("initialize", {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "test-client" },
  });

  assert.equal(res.jsonrpc, "2.0");
  assert.equal(res.id, 1);
  assert.equal(res.result.protocolVersion, "2024-11-05");
  assert.deepStrictEqual(res.result.capabilities, { tools: {} });
  assert.equal(res.result.serverInfo.name, "gemini-analyzer");
  assert.match(res.result.serverInfo.version, /^\d+\.\d+\.\d+$/);
});

// ─── 2. Tool Listing ────────────────────────────────────────────────────────

test("tools/list returns exactly 3 tools with correct schemas", async () => {
  const res = await send("tools/list");

  assert.equal(res.result.tools.length, 3);

  const names = res.result.tools.map((t) => t.name).sort();
  assert.deepStrictEqual(names, [
    "analyze_page_content",
    "extract_curriculum_data",
    "summarize_for_module",
  ]);

  // Each tool must have name, description, inputSchema.
  for (const tool of res.result.tools) {
    assert.ok(typeof tool.name === "string");
    assert.ok(typeof tool.description === "string");
    assert.ok(tool.inputSchema && tool.inputSchema.type === "object");
    assert.ok(tool.inputSchema.properties);
    assert.ok(Array.isArray(tool.inputSchema.required));
  }
});

test("analyze_page_content tool requires 'content' parameter", async () => {
  const res = await send("tools/list");
  const tool = res.result.tools.find((t) => t.name === "analyze_page_content");
  assert.ok(tool.inputSchema.required.includes("content"));
});

test("summarize_for_module requires 'content' and 'module_code'", async () => {
  const res = await send("tools/list");
  const tool = res.result.tools.find((t) => t.name === "summarize_for_module");
  assert.ok(tool.inputSchema.required.includes("content"));
  assert.ok(tool.inputSchema.required.includes("module_code"));
});

// ─── 3–5. Tool calls with missing API key ───────────────────────────────────

test("analyze_page_content returns error when API key is missing", async () => {
  delete process.env.GEMINI_API_KEY;

  const res = await send("tools/call", {
    name: "analyze_page_content",
    arguments: { content: "Some educational text about physics." },
  });

  assert.equal(res.result.isError, true);
  const body = JSON.parse(res.result.content[0].text);
  assert.ok(body.error.includes("GEMINI_API_KEY"));
});

test("extract_curriculum_data returns error when API key is missing", async () => {
  delete process.env.GEMINI_API_KEY;

  const res = await send("tools/call", {
    name: "extract_curriculum_data",
    arguments: { content: "Some content about membrane potentials." },
  });

  assert.equal(res.result.isError, true);
  const body = JSON.parse(res.result.content[0].text);
  assert.ok(body.error.includes("GEMINI_API_KEY"));
});

test("summarize_for_module returns error when API key is missing", async () => {
  delete process.env.GEMINI_API_KEY;

  const res = await send("tools/call", {
    name: "summarize_for_module",
    arguments: { content: "Linear algebra content", module_code: "MT-M1" },
  });

  assert.equal(res.result.isError, true);
  const body = JSON.parse(res.result.content[0].text);
  assert.ok(body.error.includes("GEMINI_API_KEY"));
});

// ─── 6. Missing API key does not crash ──────────────────────────────────────

test("server does not crash when GEMINI_API_KEY is absent", async () => {
  delete process.env.GEMINI_API_KEY;

  // Multiple calls should all succeed (return error responses, not throw).
  for (let i = 0; i < 3; i++) {
    const res = await send("tools/call", {
      name: "analyze_page_content",
      arguments: { content: "test" },
    }, i + 10);

    assert.equal(res.jsonrpc, "2.0");
    assert.equal(res.id, i + 10);
    assert.ok(res.result); // No crash.
  }
});

// ─── 7. Empty/undefined content → graceful error ────────────────────────────

test("analyze_page_content rejects empty content", async () => {
  const res = await send("tools/call", {
    name: "analyze_page_content",
    arguments: { content: "" },
  });

  assert.equal(res.result.isError, true);
  const body = JSON.parse(res.result.content[0].text);
  assert.ok(body.error.includes("content"));
});

test("analyze_page_content rejects missing content", async () => {
  const res = await send("tools/call", {
    name: "analyze_page_content",
    arguments: {},
  });

  assert.equal(res.result.isError, true);
  const body = JSON.parse(res.result.content[0].text);
  assert.ok(body.error.includes("content"));
});

test("extract_curriculum_data rejects whitespace-only content", async () => {
  const res = await send("tools/call", {
    name: "extract_curriculum_data",
    arguments: { content: "   " },
  });

  assert.equal(res.result.isError, true);
});

test("summarize_for_module rejects missing module_code", async () => {
  const res = await send("tools/call", {
    name: "summarize_for_module",
    arguments: { content: "Some text" },
  });

  assert.equal(res.result.isError, true);
  const body = JSON.parse(res.result.content[0].text);
  assert.ok(body.error.includes("module_code"));
});

test("summarize_for_module rejects empty module_code", async () => {
  const res = await send("tools/call", {
    name: "summarize_for_module",
    arguments: { content: "Some text", module_code: "" },
  });

  assert.equal(res.result.isError, true);
});

// ─── 8. Invalid JSON-RPC ────────────────────────────────────────────────────

test("malformed JSON returns parse error -32700", async () => {
  const raw = await mcp.handleMessage("{not valid json");
  const res = JSON.parse(raw);

  assert.equal(res.error.code, -32700);
  assert.ok(res.error.message.includes("Parse error"));
});

test("missing jsonrpc field returns invalid request -32600", async () => {
  const raw = await mcp.handleMessage(JSON.stringify({ id: 1, method: "initialize" }));
  const res = JSON.parse(raw);

  assert.equal(res.error.code, -32600);
});

test("wrong jsonrpc version returns invalid request -32600", async () => {
  const raw = await mcp.handleMessage(JSON.stringify({ jsonrpc: "1.0", id: 1, method: "initialize" }));
  const res = JSON.parse(raw);

  assert.equal(res.error.code, -32600);
});

test("missing method returns invalid request -32600", async () => {
  const raw = await mcp.handleMessage(JSON.stringify({ jsonrpc: "2.0", id: 1 }));
  const res = JSON.parse(raw);

  assert.equal(res.error.code, -32600);
});

// ─── 9. Unknown method → -32601 ────────────────────────────────────────────

test("unknown method returns method not found -32601", async () => {
  const res = await send("nonexistent/method");

  assert.equal(res.error.code, -32601);
  assert.ok(res.error.message.includes("Method not found"));
});

test("unknown tool name returns method not found in tool call", async () => {
  const res = await send("tools/call", {
    name: "nonexistent_tool",
    arguments: { content: "test" },
  });

  assert.equal(res.error.code, -32601);
  assert.ok(res.error.message.includes("Unknown tool"));
});

// ─── 10. Notifications (no id) → no response ───────────────────────────────

test("notification (no id) returns null response", async () => {
  const raw = await mcp.handleMessage(
    JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized" })
  );
  assert.equal(raw, null);
});

// ─── 11. Ping method ────────────────────────────────────────────────────────

test("ping method returns empty result", async () => {
  const res = await send("ping");
  assert.deepStrictEqual(res.result, {});
});

// ─── 12. Content chunking ───────────────────────────────────────────────────

test("chunkContent returns single chunk for short text", () => {
  const chunks = mcp.chunkContent("Hello world", 100);
  assert.equal(chunks.length, 1);
  assert.equal(chunks[0], "Hello world");
});

test("chunkContent splits long text at paragraph boundaries", () => {
  const paragraph1 = "A".repeat(60);
  const paragraph2 = "B".repeat(60);
  const text = `${paragraph1}\n\n${paragraph2}`;
  const chunks = mcp.chunkContent(text, 80);

  assert.ok(chunks.length >= 2);
  assert.ok(chunks[0].length <= 80 || chunks[0].includes(paragraph1));
});

test("chunkContent handles text without good break points", () => {
  const text = "X".repeat(300);
  const chunks = mcp.chunkContent(text, 100);

  assert.ok(chunks.length >= 3);
  // Every chunk should be <= 100 chars.
  for (const chunk of chunks) {
    assert.ok(chunk.length <= 100);
  }
});

// ─── 13. Duplicate detection ────────────────────────────────────────────────

test("contentHash returns consistent hex string", () => {
  const h1 = mcp.contentHash("test content");
  const h2 = mcp.contentHash("test content");
  assert.equal(h1, h2);
  assert.match(h1, /^[0-9a-f]{16}$/);
});

test("contentHash produces different hashes for different content", () => {
  const h1 = mcp.contentHash("content A");
  const h2 = mcp.contentHash("content B");
  assert.notEqual(h1, h2);
});

test("isDuplicate flags repeated content", () => {
  mcp._resetDuplicates();

  const text = "unique text " + randomUUID();
  assert.equal(mcp.isDuplicate(text), false);
  assert.equal(mcp.isDuplicate(text), true); // Second time = duplicate.
});

test("isDuplicate allows different content", () => {
  mcp._resetDuplicates();

  assert.equal(mcp.isDuplicate("text-A-" + randomUUID()), false);
  assert.equal(mcp.isDuplicate("text-B-" + randomUUID()), false);
});

// ─── 14. Config loading ─────────────────────────────────────────────────────

test("loadConfig returns valid defaults", () => {
  const cfg = mcp.loadConfig();
  assert.ok(typeof cfg.model === "string");
  assert.ok(typeof cfg.temperature === "number");
  assert.ok(typeof cfg.maxOutputTokens === "number");
  assert.ok(typeof cfg.requestTimeoutMs === "number");
  assert.ok(typeof cfg.maxRetries === "number");
  assert.ok(typeof cfg.retryBaseDelayMs === "number");
  assert.ok(typeof cfg.maxContentChars === "number");
  assert.ok(cfg.maxRetries >= 1);
  assert.ok(cfg.requestTimeoutMs >= 1000);
});

// ─── 15. Tool handlers are functions ────────────────────────────────────────

test("all TOOL_HANDLERS are async functions", () => {
  for (const [name, handler] of Object.entries(mcp.TOOL_HANDLERS)) {
    assert.equal(typeof handler, "function", `Handler ${name} must be a function`);
  }
});

test("TOOLS array matches TOOL_HANDLERS keys", () => {
  const toolNames = mcp.TOOLS.map((t) => t.name).sort();
  const handlerNames = Object.keys(mcp.TOOL_HANDLERS).sort();
  assert.deepStrictEqual(toolNames, handlerNames);
});

// ─── 16. Duplicate detection in analyze_page_content ────────────────────────

test("analyze_page_content returns duplicate flag for repeated content", async () => {
  mcp._resetDuplicates();
  delete process.env.GEMINI_API_KEY;

  // First call: will fail with API key error (but content hash is recorded).
  // We need to test with a key set, but since this is unit test, we test the
  // duplicate detection path which returns before API call.

  // Set a fake key to reach duplicate logic.
  process.env.GEMINI_API_KEY = "test-key-not-real";

  // The first call will fail at network level, but the hash is stored.
  // For duplicate test, call with same content — should return duplicate before API call.
  const uniqueContent = "Duplicate test content " + randomUUID();

  // Mark content as seen via isDuplicate.
  mcp.isDuplicate(uniqueContent);

  // Now call via protocol — should detect duplicate.
  const res = await send("tools/call", {
    name: "analyze_page_content",
    arguments: { content: uniqueContent },
  });

  const body = JSON.parse(res.result.content[0].text);
  assert.equal(body.duplicate, true);
  assert.ok(body.content_hash);

  // Cleanup
  delete process.env.GEMINI_API_KEY;
  mcp._resetDuplicates();
});

// ─── 17. Concurrent request isolation ───────────────────────────────────────

test("concurrent handleMessage calls are isolated", async () => {
  const promises = [
    send("initialize", { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "c1" } }, 100),
    send("tools/list", undefined, 200),
    send("ping", undefined, 300),
  ];

  const results = await Promise.all(promises);

  assert.equal(results[0].id, 100);
  assert.ok(results[0].result.protocolVersion);

  assert.equal(results[1].id, 200);
  assert.ok(Array.isArray(results[1].result.tools));

  assert.equal(results[2].id, 300);
  assert.deepStrictEqual(results[2].result, {});
});

// ─── 18. Message ID types ───────────────────────────────────────────────────

test("string IDs are preserved in responses", async () => {
  const res = await send("ping", undefined, "my-string-id");
  assert.equal(res.id, "my-string-id");
});

test("numeric IDs are preserved in responses", async () => {
  const res = await send("ping", undefined, 42);
  assert.equal(res.id, 42);
});

// ─── 19. tools/call with missing params ─────────────────────────────────────

test("tools/call with no name returns error", async () => {
  const res = await send("tools/call", {});
  assert.equal(res.error.code, -32602);
});

test("tools/call with null name returns error", async () => {
  const res = await send("tools/call", { name: null });
  assert.equal(res.error.code, -32602);
});

// ─── Cleanup ─────────────────────────────────────────────────────────────────

test.after(() => {
  // Restore original API key if it existed.
  if (ORIGINAL_KEY) {
    process.env.GEMINI_API_KEY = ORIGINAL_KEY;
  }
  mcp._resetDuplicates();
});
