import { useState, useEffect } from "react";
import { listSectors } from "../services/api";
import Spinner from "./Spinner";

const STORAGE_KEY = "sector-rag-recent-sectors";

function loadRecentSectors(): string[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveRecentSector(sector: string) {
  try {
    const recent = loadRecentSectors();
    if (!recent.includes(sector)) {
      recent.unshift(sector);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(recent.slice(0, 10)));
    }
  } catch {
    // localStorage pode estar indisponível
  }
}



interface SectorSelectorProps {
  onSectorSelected: (sector: string) => void;
}

export default function SectorSelector({ onSectorSelected }: SectorSelectorProps) {
  const [sectors, setSectors] = useState<string[]>([]);
  const [recentSectors, setRecentSectors] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showNewInput, setShowNewInput] = useState(false);
  const [newSector, setNewSector] = useState("");

  useEffect(() => {
    setRecentSectors(loadRecentSectors());

    let cancelled = false;
    async function fetchSectors() {
      try {
        const data = await listSectors();
        if (!cancelled) {
          setSectors(data);
          setError(null);
        }
      } catch {
        if (!cancelled) setError("Não foi possível carregar setores");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    fetchSectors();
    return () => { cancelled = true; };
  }, []);

  function allSectors(): string[] {
    const seen = new Set<string>();
    const result: string[] = [];
    for (const s of sectors) {
      if (!seen.has(s)) { seen.add(s); result.push(s); }
    }
    for (const s of recentSectors) {
      if (!seen.has(s)) { seen.add(s); result.push(s); }
    }
    return result;
  }

  function handleSelect(sector: string) {
    saveRecentSector(sector);
    onSectorSelected(sector);
  }

  function handleCreateNew(e: React.FormEvent) {
    e.preventDefault();
    const s = newSector.trim();
    if (!s) return;
    saveRecentSector(s);
    onSectorSelected(s);
  }

  return (
    <div className="sector-selector">
      {/* Header estilo WhatsApp */}
      <div className="sector-header">
        <h1 className="sector-header-title">Sector-RAG</h1>
        <span className="sector-header-sub">Selecione um setor</span>
      </div>

      {/* Barra de pesquisa / novo setor */}
      <div className="sector-toolbar">
        {!showNewInput ? (
          <button className="sector-new-btn" onClick={() => setShowNewInput(true)}>
            <span className="sector-new-icon">+</span>
            Novo setor
          </button>
        ) : (
          <form onSubmit={handleCreateNew} className="sector-new-form">
            <input
              className="sector-new-input"
              type="text"
              placeholder="Nome do novo setor..."
              value={newSector}
              onChange={(e) => setNewSector(e.target.value)}
              autoFocus
            />
            <button type="submit" className="sector-new-confirm" disabled={!newSector.trim()}>
              Criar
            </button>
            <button
              type="button"
              className="sector-new-cancel"
              onClick={() => { setShowNewInput(false); setNewSector(""); }}
            >
              Cancelar
            </button>
          </form>
        )}
      </div>

      {/* Loading */}
      {loading && (
        <div className="sector-loading-state">
          <Spinner text="Carregando setores..." />
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="sector-error">{error}</div>
      )}

      {/* Lista de setores estilo WhatsApp */}
      {!loading && (
        <div className="sector-list">
          {allSectors().length === 0 ? (
            <div className="sector-empty">
              <p>Nenhum setor encontrado</p>
              <p className="sector-empty-hint">Crie um novo setor acima para começar</p>
            </div>
          ) : (
            allSectors().map((s) => (
              <button
                key={s}
                className="sector-list-item"
                onClick={() => handleSelect(s)}
              >
                <span className="sector-list-avatar">{s.charAt(0).toUpperCase()}</span>
                <div className="sector-list-info">
                  <span className="sector-list-name">{s}</span>
                  <span className="sector-list-status">
                    {sectors.includes(s) ? "Documentos indexados" : "Setor recente"}
                  </span>
                </div>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
