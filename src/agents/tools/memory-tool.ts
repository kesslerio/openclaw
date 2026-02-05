import { Type } from "@sinclair/typebox";
import type { OpenClawConfig } from "../../config/config.js";
import type { MemoryCitationsMode } from "../../config/types.memory.js";
import type { MemorySearchResult, MemorySearchMode } from "../../memory/types.js";
import type { AnyAgentTool } from "./common.js";
import { resolveMemoryBackendConfig } from "../../memory/backend-config.js";
import { getMemorySearchManager } from "../../memory/index.js";
import { parseAgentSessionKey } from "../../routing/session-key.js";
import { resolveSessionAgentId } from "../agent-scope.js";
import { resolveMemorySearchConfig } from "../memory-search.js";
import { jsonResult, readNumberParam, readStringParam, readStringArrayParam } from "./common.js";

const MemorySearchSchema = Type.Object({
  query: Type.String(),
  maxResults: Type.Optional(Type.Number()),
  minScore: Type.Optional(Type.Number()),
  mode: Type.Optional(Type.String()), // "index" (default, compact ~50 tokens/result) | "full" (legacy, ~500 tokens/result)
});

const MemoryGetSchema = Type.Object({
  path: Type.String(),
  from: Type.Optional(Type.Number()),
  lines: Type.Optional(Type.Number()),
});

const MemoryGetChunksSchema = Type.Object({
  ids: Type.Array(Type.String()), // Chunk IDs from memory_search index results
});

const MemoryTimelineSchema = Type.Object({
  id: Type.Optional(Type.String()), // Chunk ID to get context around
  path: Type.Optional(Type.String()), // Or specify path + line
  line: Type.Optional(Type.Number()),
  context: Type.Optional(Type.Number()), // Number of surrounding chunks (default: 3)
});

export function createMemorySearchTool(options: {
  config?: OpenClawConfig;
  agentSessionKey?: string;
}): AnyAgentTool | null {
  const cfg = options.config;
  if (!cfg) {
    return null;
  }
  const agentId = resolveSessionAgentId({
    sessionKey: options.agentSessionKey,
    config: cfg,
  });
  if (!resolveMemorySearchConfig(cfg, agentId)) {
    return null;
  }
  return {
    label: "Memory Search",
    name: "memory_search",
    description:
      'Mandatory recall step: semantically search MEMORY.md + memory/*.md (and optional session transcripts). Use mode="index" (default) for compact results (~50 tokens each) with IDs, then memory_get_chunks to fetch full details for relevant IDs. Use mode="full" for legacy behavior (~500 tokens each). Progressive disclosure saves ~10x tokens.',
    parameters: MemorySearchSchema,
    execute: async (_toolCallId, params) => {
      const query = readStringParam(params, "query", { required: true });
      const maxResults = readNumberParam(params, "maxResults");
      const minScore = readNumberParam(params, "minScore");
      const modeParam = readStringParam(params, "mode");
      const mode: MemorySearchMode = modeParam === "full" ? "full" : "index";
      const { manager, error } = await getMemorySearchManager({
        cfg,
        agentId,
      });
      if (!manager) {
        return jsonResult({ results: [], disabled: true, error });
      }
      try {
        const citationsMode = resolveMemoryCitationsMode(cfg);
        const includeCitations = shouldIncludeCitations({
          mode: citationsMode,
          sessionKey: options.agentSessionKey,
        });
        const status = manager.status();

        if (mode === "index" && typeof manager.searchIndex === "function") {
          // Progressive disclosure: return compact index with IDs
          const indexResults = await manager.searchIndex(query, {
            maxResults,
            minScore,
            sessionKey: options.agentSessionKey,
          });
          return jsonResult({
            mode: "index",
            hint: "Use memory_get_chunks with IDs to fetch full details for relevant results",
            results: indexResults,
            provider: status.provider,
            model: status.model,
            fallback: status.fallback,
          });
        }

        // Legacy full mode
        const rawResults = await manager.search(query, {
          maxResults,
          minScore,
          sessionKey: options.agentSessionKey,
        });
        const decorated = decorateCitations(rawResults, includeCitations);
        const resolved = resolveMemoryBackendConfig({ cfg, agentId });
        const results =
          status.backend === "qmd"
            ? clampResultsByInjectedChars(decorated, resolved.qmd?.limits.maxInjectedChars)
            : decorated;
        return jsonResult({
          mode: "full",
          results,
          provider: status.provider,
          model: status.model,
          fallback: status.fallback,
          citations: citationsMode,
        });
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        return jsonResult({ results: [], disabled: true, error: message });
      }
    },
  };
}

export function createMemoryGetTool(options: {
  config?: OpenClawConfig;
  agentSessionKey?: string;
}): AnyAgentTool | null {
  const cfg = options.config;
  if (!cfg) {
    return null;
  }
  const agentId = resolveSessionAgentId({
    sessionKey: options.agentSessionKey,
    config: cfg,
  });
  if (!resolveMemorySearchConfig(cfg, agentId)) {
    return null;
  }
  return {
    label: "Memory Get",
    name: "memory_get",
    description:
      "Safe snippet read from MEMORY.md or memory/*.md with optional from/lines; use after memory_search to pull only the needed lines and keep context small.",
    parameters: MemoryGetSchema,
    execute: async (_toolCallId, params) => {
      const relPath = readStringParam(params, "path", { required: true });
      const from = readNumberParam(params, "from", { integer: true });
      const lines = readNumberParam(params, "lines", { integer: true });
      const { manager, error } = await getMemorySearchManager({
        cfg,
        agentId,
      });
      if (!manager) {
        return jsonResult({ path: relPath, text: "", disabled: true, error });
      }
      try {
        const result = await manager.readFile({
          relPath,
          from: from ?? undefined,
          lines: lines ?? undefined,
        });
        return jsonResult(result);
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        return jsonResult({ path: relPath, text: "", disabled: true, error: message });
      }
    },
  };
}

export function createMemoryGetChunksTool(options: {
  config?: OpenClawConfig;
  agentSessionKey?: string;
}): AnyAgentTool | null {
  const cfg = options.config;
  if (!cfg) {
    return null;
  }
  const agentId = resolveSessionAgentId({
    sessionKey: options.agentSessionKey,
    config: cfg,
  });
  if (!resolveMemorySearchConfig(cfg, agentId)) {
    return null;
  }
  return {
    label: "Memory Get Chunks",
    name: "memory_get_chunks",
    description:
      "Fetch full details for specific chunk IDs from memory_search index results. Use this after memory_search(mode='index') to get complete text for relevant chunks. Batch multiple IDs in one call to minimize round-trips.",
    parameters: MemoryGetChunksSchema,
    execute: async (_toolCallId, params) => {
      const ids = readStringArrayParam(params, "ids");
      if (!ids || ids.length === 0) {
        return jsonResult({ chunks: [], error: "ids required" });
      }
      const { manager, error } = await getMemorySearchManager({
        cfg,
        agentId,
      });
      if (!manager) {
        return jsonResult({ chunks: [], disabled: true, error });
      }
      if (typeof manager.getChunks !== "function") {
        return jsonResult({
          chunks: [],
          disabled: true,
          error: "memory_get_chunks not supported by this memory backend",
        });
      }
      try {
        const chunks = await manager.getChunks(ids);
        return jsonResult({
          chunks,
          count: chunks.length,
          requested: ids.length,
        });
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        return jsonResult({ chunks: [], disabled: true, error: message });
      }
    },
  };
}

export function createMemoryTimelineTool(options: {
  config?: OpenClawConfig;
  agentSessionKey?: string;
}): AnyAgentTool | null {
  const cfg = options.config;
  if (!cfg) {
    return null;
  }
  const agentId = resolveSessionAgentId({
    sessionKey: options.agentSessionKey,
    config: cfg,
  });
  if (!resolveMemorySearchConfig(cfg, agentId)) {
    return null;
  }
  return {
    label: "Memory Timeline",
    name: "memory_timeline",
    description:
      "Get chronological context around a specific memory chunk. Useful after memory_search to understand what happened before/after a result. Provide either a chunk ID, or a path + line number.",
    parameters: MemoryTimelineSchema,
    execute: async (_toolCallId, params) => {
      const id = readStringParam(params, "id");
      const path = readStringParam(params, "path");
      const line = readNumberParam(params, "line", { integer: true });
      const context = readNumberParam(params, "context", { integer: true });

      if (!id && !path) {
        return jsonResult({ entries: [], error: "Provide either id or path+line" });
      }

      const { manager, error } = await getMemorySearchManager({
        cfg,
        agentId,
      });
      if (!manager) {
        return jsonResult({ entries: [], disabled: true, error });
      }
      if (typeof manager.getTimeline !== "function") {
        return jsonResult({
          entries: [],
          disabled: true,
          error: "memory_timeline not supported by this memory backend",
        });
      }
      try {
        const entries = await manager.getTimeline({
          id: id ?? undefined,
          path: path ?? undefined,
          line: line ?? undefined,
          context: context ?? undefined,
        });
        return jsonResult({
          entries,
          count: entries.length,
          target: id ?? `${path}:${line}`,
        });
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        return jsonResult({ entries: [], disabled: true, error: message });
      }
    },
  };
}

function resolveMemoryCitationsMode(cfg: OpenClawConfig): MemoryCitationsMode {
  const mode = cfg.memory?.citations;
  if (mode === "on" || mode === "off" || mode === "auto") {
    return mode;
  }
  return "auto";
}

function decorateCitations(results: MemorySearchResult[], include: boolean): MemorySearchResult[] {
  if (!include) {
    return results.map((entry) => ({ ...entry, citation: undefined }));
  }
  return results.map((entry) => {
    const citation = formatCitation(entry);
    const snippet = `${entry.snippet.trim()}\n\nSource: ${citation}`;
    return { ...entry, citation, snippet };
  });
}

function formatCitation(entry: MemorySearchResult): string {
  const lineRange =
    entry.startLine === entry.endLine
      ? `#L${entry.startLine}`
      : `#L${entry.startLine}-L${entry.endLine}`;
  return `${entry.path}${lineRange}`;
}

function clampResultsByInjectedChars(
  results: MemorySearchResult[],
  budget?: number,
): MemorySearchResult[] {
  if (!budget || budget <= 0) {
    return results;
  }
  let remaining = budget;
  const clamped: MemorySearchResult[] = [];
  for (const entry of results) {
    if (remaining <= 0) {
      break;
    }
    const snippet = entry.snippet ?? "";
    if (snippet.length <= remaining) {
      clamped.push(entry);
      remaining -= snippet.length;
    } else {
      const trimmed = snippet.slice(0, Math.max(0, remaining));
      clamped.push({ ...entry, snippet: trimmed });
      break;
    }
  }
  return clamped;
}

function shouldIncludeCitations(params: {
  mode: MemoryCitationsMode;
  sessionKey?: string;
}): boolean {
  if (params.mode === "on") {
    return true;
  }
  if (params.mode === "off") {
    return false;
  }
  // auto: show citations in direct chats; suppress in groups/channels by default.
  const chatType = deriveChatTypeFromSessionKey(params.sessionKey);
  return chatType === "direct";
}

function deriveChatTypeFromSessionKey(sessionKey?: string): "direct" | "group" | "channel" {
  const parsed = parseAgentSessionKey(sessionKey);
  if (!parsed?.rest) {
    return "direct";
  }
  const tokens = new Set(parsed.rest.toLowerCase().split(":").filter(Boolean));
  if (tokens.has("channel")) {
    return "channel";
  }
  if (tokens.has("group")) {
    return "group";
  }
  return "direct";
}
