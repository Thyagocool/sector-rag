import { useState, useEffect } from "react";
import { listSectors } from "../services/api";

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
  const [input, setInput] = useState("");
  const [sectors, setSectors] = useState<string[]>([]);
  const [recentSectors, setRecentSectors] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<"select" | "new">("select");

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

  /** Junta setores da API + recentes, sem duplicatas, ordenados */
  function allSectors(): string[] {
    const seen = new Set<string>();
    const result: string[] = [];
    // Primeiro os setores com documentos (API)
    for (const s of sectors) {
      if (!seen.has(s)) {
        seen.add(s);
        result.push(s);
      }
    }
    // Depois os recentes que nao estao na API
    for (const s of recentSectors) {
      if (!seen.has(s)) {
        seen.add(s);
        result.push(s);
      }
    }
    return result;
  }

  function handleSelectChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const val = e.target.value;
    if (val === "__new__") {
      setMode("new");
      setInput("");
    } else if (val) {
      setInput(val);
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const s = input.trim();
    if (!s) return;
    saveRecentSector(s);
    onSectorSelected(s);
  }

  return (
    <div className="sector-selector">
      <div className="sector-card">
        <h1 className="sector-title">Sector-RAG</h1>
        <p className="sector-subtitle">
          Assistente de documentos por setor
        </p>

        {error && (
          <div className="sector-error">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="sector-form">
          <label htmlFor="sector-select" className="sector-label">
            Qual setor você quer acessar?
          </label>

          {loading ? (
            <div className="sector-loading-wrapper">
              <span className="sector-loading" />
              Carregando setores...
            </div>
          ) : (
            <>
              {mode === "select" && (
                <select
                  id="sector-select"
                  className="sector-select"
                  value={input}
                  onChange={handleSelectChange}
                >
                  <option value="" disabled>
                    {allSectors().length > 0
                      ? "— Escolha um setor —"
                      : "— Nenhum setor encontrado —"}
                  </option>
                  {allSectors().map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                  <option value="__new__">+ Novo setor...</option>
                </select>
              )}

              {mode === "new" && (
                <div className="sector-input-wrapper">
                  <input
                    id="sector-input"
                    className="sector-input"
                    type="text"
                    placeholder="Digite o nome do novo setor"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    autoFocus
                  />
                  <button
                    type="button"
                    className="sector-back-btn"
                    onClick={() => { setMode("select"); setInput(""); }}
                    title="Voltar para setores existentes"
                  >
                    ←
                  </button>
                </div>
              )}
            </>
          )}

          {mode === "select" && input && (
            <p className="sector-selected-label">
              Setor selecionado: <strong>{input}</strong>
            </p>
          )}

          <button
            className="btn btn-sector"
            type="submit"
            disabled={!input.trim()}
          >
            {mode === "select" && input ? "Acessar setor" : "Criar e acessar"}
          </button>
        </form>
      </div>
    </div>
  );
}
