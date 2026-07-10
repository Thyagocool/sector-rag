/// Camada de comunicacao com o backend Sector-RAG.

const API_BASE = "/api/v1";

// ─── Tipos ──────────────────────────────────────────────────────────────────

export interface Source {
  content: string;
  metadata: Record<string, unknown>;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
}

export interface HealthResponse {
  status: string;
  app: string;
  version: string;
  vector_collections: string[];
}

export interface UploadResponse {
  message: string;
  documents_processed: number;
}

export interface ChunkInfo {
  id: string;
  content: string;
  metadata: Record<string, unknown>;
}

export interface SubTopic {
  subtopic: string;
  snippet: string;
  content: string;
}

export interface FileTopic {
  topic: string;
  snippet: string;
  subtopics: SubTopic[];
}

export interface FileInfo {
  filename: string;
  topics: FileTopic[];
}

export interface TopicChunk {
  chunk_id: string;
  content: string;
}

export interface TopicChunksResponse {
  topic: string;
  chunks: TopicChunk[];
}

// ─── RAG: perguntas ─────────────────────────────────────────────────────────

export async function ask(
  question: string,
  sector: string,
  source?: string,
  topic?: string,
): Promise<AskResponse> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 120_000); // 2min timeout

  try {
    const res = await fetch(`${API_BASE}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, sector, source, topic }),
      signal: controller.signal,
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Erro ${res.status}: ${text}`);
    }
    return res.json();
  } finally {
    clearTimeout(timeout);
  }
}

export async function* askStream(
  question: string,
  sector: string,
  source?: string,
  topic?: string,
): AsyncGenerator<string> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 120_000); // 2min timeout

  try {
    const res = await fetch(`${API_BASE}/ask/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, sector, source, topic }),
      signal: controller.signal,
    });
    if (!res.ok) throw new Error(`Erro ${res.status}`);

    const reader = res.body?.getReader();
    if (!reader) throw new Error("Sem stream disponivel");

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith("data: ")) {
          const payload = trimmed.slice(6);
          if (payload === "[DONE]") return;
          try {
            const parsed = JSON.parse(payload);
            if (parsed.token) {
              yield parsed.token;
            } else if (parsed.error) {
              throw new Error(parsed.error);
            }
          } catch {
            // ignora linhas mal formatadas
          }
        }
      }
    }
  } finally {
    clearTimeout(timeout);
  }
}

// ─── Documentos ─────────────────────────────────────────────────────────────

export async function uploadDocument(file: File, sector: string): Promise<UploadResponse> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 600_000); // 10min timeout

  const form = new FormData();
  form.append("file", file);
  form.append("sector", sector);

  try {
    const res = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: form,
      signal: controller.signal,
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Erro ${res.status}: ${text}`);
    }
    return res.json();
  } finally {
    clearTimeout(timeout);
  }
}

// ─── Setor / Arquivos ────────────────────────────────────────────────────────

export async function listSectors(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/sectors`);
  if (!res.ok) throw new Error(`Erro ${res.status}`);
  return res.json();
}

export async function listFiles(sector: string): Promise<FileInfo[]> {
  const res = await fetch(`${API_BASE}/sector/files?sector=${encodeURIComponent(sector)}`);
  if (!res.ok) throw new Error(`Erro ${res.status}`);
  return res.json();
}

export async function listTopicChunks(
  sector: string,
  file: string,
  topic: string,
): Promise<TopicChunksResponse> {
  const params = new URLSearchParams({
    sector,
    file,
    topic,
  });
  const res = await fetch(`${API_BASE}/sector/topic/chunks?${params}`);
  if (!res.ok) throw new Error(`Erro ${res.status}`);
  return res.json();
}

// ─── Admin ───────────────────────────────────────────────────────────────────

export async function listChunks(sector: string): Promise<ChunkInfo[]> {
  const res = await fetch(`${API_BASE}/admin/chunks?sector=${encodeURIComponent(sector)}`);
  if (!res.ok) throw new Error(`Erro ${res.status}`);
  return res.json();
}

export async function clearSector(sector: string): Promise<void> {
  const res = await fetch(`${API_BASE}/admin/chunks`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sector }),
  });
  if (!res.ok) throw new Error(`Erro ${res.status}`);
}

// ─── Health ─────────────────────────────────────────────────────────────────

export async function health(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Erro ${res.status}`);
  return res.json();
}
