import { useState, useEffect, useRef } from "react";
import { listSectors } from "../services/api";

interface SectorSelectorProps {
  onSectorSelected: (sector: string) => void;
}

export default function SectorSelector({ onSectorSelected }: SectorSelectorProps) {
  const [input, setInput] = useState("");
  const [sectors, setSectors] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
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

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const s = input.trim();
    if (!s) return;
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
          <label htmlFor="sector-input" className="sector-label">
            Qual setor você quer acessar?
          </label>

          <div className="sector-input-wrapper">
            <input
              ref={inputRef}
              id="sector-input"
              className="sector-input"
              type="text"
              placeholder="Ex: RH, Jurídico, Financeiro..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              autoFocus
              list="sector-list"
              autoComplete="off"
            />
            {!loading && sectors.length > 0 && (
              <datalist id="sector-list">
                {sectors.map((s) => (
                  <option key={s} value={s} />
                ))}
              </datalist>
            )}
            {loading && (
              <span className="sector-loading" title="Carregando setores...">
                ↻
              </span>
            )}
          </div>

          {!loading && sectors.length > 0 && input.length > 0 && (
            <div className="sector-suggestions-label">
              Setores existentes: {sectors.join(", ")}
            </div>
          )}

          <button
            className="btn btn-sector"
            type="submit"
            disabled={!input.trim()}
          >
            Acessar setor
          </button>
        </form>
      </div>
    </div>
  );
}
