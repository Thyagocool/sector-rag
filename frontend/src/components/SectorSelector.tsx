import { useState } from "react";

interface SectorSelectorProps {
  onSectorSelected: (sector: string) => void;
}

export default function SectorSelector({ onSectorSelected }: SectorSelectorProps) {
  const [input, setInput] = useState("");

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
        <form onSubmit={handleSubmit} className="sector-form">
          <label htmlFor="sector-input" className="sector-label">
            Qual setor você quer acessar?
          </label>
          <input
            id="sector-input"
            className="sector-input"
            type="text"
            placeholder="Ex: RH, Jurídico, Financeiro..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            autoFocus
          />
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
