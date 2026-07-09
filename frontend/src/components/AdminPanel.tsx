import { useState, useEffect, useCallback } from "react";
import { listChunks, clearSector, type ChunkInfo } from "../services/api";

interface AdminPanelProps {
  sector: string;
}

export default function AdminPanel({ sector }: AdminPanelProps) {
  const [chunks, setChunks] = useState<ChunkInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [clearing, setClearing] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const loadChunks = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listChunks(sector);
      setChunks(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Erro desconhecido";
      setMessage(`Erro ao carregar chunks: ${msg}`);
    } finally {
      setLoading(false);
    }
  }, [sector]);

  useEffect(() => {
    loadChunks();
  }, [loadChunks]);

  async function handleClearSector() {
    if (!confirm(`Limpar todos os chunks do setor "${sector}"?`)) return;

    setClearing(true);
    try {
      await clearSector(sector);
      setMessage(`Setor "${sector}" limpo com sucesso!`);
      setChunks([]);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Erro desconhecido";
      setMessage(`Erro ao limpar: ${msg}`);
    } finally {
      setClearing(false);
    }
  }

  return (
    <div className="admin-panel">
      <div className="admin-header">
        <h2>Admin - Setor: {sector}</h2>
        <button
          className="btn btn-danger"
          onClick={handleClearSector}
          disabled={clearing || chunks.length === 0}
        >
          {clearing ? "Limpando..." : `Limpar setor "${sector}"`}
        </button>
      </div>

      {message && (
        <div className="admin-message">{message}</div>
      )}

      <div className="admin-stats">
        Total de chunks: {chunks.length}
      </div>

      {loading ? (
        <p>Carregando chunks...</p>
      ) : chunks.length === 0 ? (
        <p className="admin-empty">
          Nenhum chunk encontrado para o setor "{sector}".
        </p>
      ) : (
        <div className="admin-chunks">
          {chunks.map((chunk, i) => (
            <div key={chunk.id || i} className="admin-chunk-card">
              <div className="chunk-header">
                <span className="chunk-id">#{chunk.id?.slice(0, 12) || i + 1}</span>
                {chunk.metadata?.source && (
                  <span className="chunk-source">
                    {String(chunk.metadata.source)}
                  </span>
                )}
              </div>
              <p className="chunk-preview">
                {chunk.content.slice(0, 300)}
                {chunk.content.length > 300 ? "..." : ""}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
