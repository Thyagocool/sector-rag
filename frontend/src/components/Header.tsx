import { useState, useRef } from "react";
import { uploadDocument } from "../services/api";

interface HeaderProps {
  sector: string;
  onChangeSector: () => void;
  onUploadDone: (msg: string) => void;
  onAdminClick: () => void;
  isAdmin: boolean;
}

export default function Header({
  sector,
  onChangeSector,
  onUploadDone,
  onAdminClick,
  isAdmin,
}: HeaderProps) {
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const res = await uploadDocument(file, sector);
      onUploadDone(
        `${file.name} indexado no setor "${sector}" (${res.documents_processed} chunks)`,
      );
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Erro no upload";
      onUploadDone(`Falha: ${msg}`);
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  return (
    <header className="header">
      <div className="header-left">
        <h1 className="header-title">Sector-RAG</h1>
        <span className="header-subtitle">Setor: {sector}</span>
      </div>

      <div className="header-right">
        <input
          ref={fileRef}
          type="file"
          accept=".pdf,.txt,.md,.docx,.html,.csv,.json,.py,.js,.ts,.sql"
          hidden
          onChange={handleFile}
        />
        <button
          className="btn btn-upload"
          disabled={uploading}
          onClick={() => fileRef.current?.click()}
          title="Upload de documento"
        >
          {uploading ? "Enviando..." : "Upload"}
        </button>

        <button
          className="btn btn-admin"
          onClick={onAdminClick}
          title={isAdmin ? "Voltar ao chat" : "Painel admin"}
        >
          {isAdmin ? "Chat" : "Admin"}
        </button>

        <button
          className="btn btn-change-sector"
          onClick={onChangeSector}
          title="Trocar setor"
        >
          Trocar setor
        </button>
      </div>
    </header>
  );
}
