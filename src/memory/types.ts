export type MemorySource = "memory" | "sessions";

export type MemorySearchMode = "index" | "full";

export type MemorySearchResult = {
  id: string;
  path: string;
  startLine: number;
  endLine: number;
  score: number;
  snippet: string;
  source: MemorySource;
  citation?: string;
};

export type MemoryIndexResult = {
  id: string;
  path: string;
  startLine: number;
  endLine: number;
  score: number;
  preview: string; // ~100 char preview
  source: MemorySource;
  tokens?: number; // estimated tokens if fetched in full
};

export type MemoryChunkDetail = {
  id: string;
  path: string;
  startLine: number;
  endLine: number;
  text: string;
  source: MemorySource;
  citation?: string;
};

export type MemoryTimelineEntry = {
  id: string;
  path: string;
  startLine: number;
  endLine: number;
  preview: string;
  source: MemorySource;
  position: "before" | "current" | "after";
  distance: number; // lines from target
};

export type MemoryEmbeddingProbeResult = {
  ok: boolean;
  error?: string;
};

export type MemorySyncProgressUpdate = {
  completed: number;
  total: number;
  label?: string;
};

export type MemoryProviderStatus = {
  backend: "builtin" | "qmd";
  provider: string;
  model?: string;
  requestedProvider?: string;
  files?: number;
  chunks?: number;
  dirty?: boolean;
  workspaceDir?: string;
  dbPath?: string;
  extraPaths?: string[];
  sources?: MemorySource[];
  sourceCounts?: Array<{ source: MemorySource; files: number; chunks: number }>;
  cache?: { enabled: boolean; entries?: number; maxEntries?: number };
  fts?: { enabled: boolean; available: boolean; error?: string };
  fallback?: { from: string; reason?: string };
  vector?: {
    enabled: boolean;
    available?: boolean;
    extensionPath?: string;
    loadError?: string;
    dims?: number;
  };
  batch?: {
    enabled: boolean;
    failures: number;
    limit: number;
    wait: boolean;
    concurrency: number;
    pollIntervalMs: number;
    timeoutMs: number;
    lastError?: string;
    lastProvider?: string;
  };
  custom?: Record<string, unknown>;
};

export interface MemorySearchManager {
  search(
    query: string,
    opts?: {
      maxResults?: number;
      minScore?: number;
      sessionKey?: string;
      mode?: MemorySearchMode;
    },
  ): Promise<MemorySearchResult[]>;
  searchIndex(
    query: string,
    opts?: { maxResults?: number; minScore?: number; sessionKey?: string },
  ): Promise<MemoryIndexResult[]>;
  getChunks(ids: string[]): Promise<MemoryChunkDetail[]>;
  getTimeline(params: {
    id?: string;
    path?: string;
    line?: number;
    context?: number;
  }): Promise<MemoryTimelineEntry[]>;
  readFile(params: {
    relPath: string;
    from?: number;
    lines?: number;
  }): Promise<{ text: string; path: string }>;
  status(): MemoryProviderStatus;
  sync?(params?: {
    reason?: string;
    force?: boolean;
    progress?: (update: MemorySyncProgressUpdate) => void;
  }): Promise<void>;
  probeEmbeddingAvailability(): Promise<MemoryEmbeddingProbeResult>;
  probeVectorAvailability(): Promise<boolean>;
  close?(): Promise<void>;
}
