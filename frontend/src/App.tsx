import { useState, useCallback } from "react";
import Header from "./components/Header";
import Chat from "./components/Chat";
import SectorSelector from "./components/SectorSelector";
import FileList from "./components/FileList";
import AdminPanel from "./components/AdminPanel";
import Toast from "./components/Toast";
import "./App.css";

export default function App() {
  const [sector, setSector] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null);
  const [view, setView] = useState<"chat" | "files" | "admin">("files");
  const [toast, setToast] = useState<{ message: string; type: "ok" | "err" } | null>(null);
  const [refreshKey, setRefreshKey] = useState(0); // incrementado a cada upload pra forçar refresh da lista

  const showToast = useCallback((msg: string, type: "ok" | "err" = "ok") => {
    setToast({ message: msg, type });
  }, []);

  function handleSectorSelected(s: string) {
    setSector(s);
    setSelectedFile(null);
    setSelectedTopic(null);
    setView("files");
    showToast(`Setor "${s}" selecionado`, "ok");
  }

  function handleFileSelected(filename: string, topic?: string) {
    setSelectedFile(filename);
    setSelectedTopic(topic ?? null);
    setView("chat");
    showToast(`Arquivo: ${filename}${topic ? ` > ${topic}` : ""}`, "ok");
  }

  function handleBackToSectors() {
    setSector(null);
    setSelectedFile(null);
    setSelectedTopic(null);
  }

  function handleBackToFiles() {
    setSelectedFile(null);
    setSelectedTopic(null);
    setView("files");
    setRefreshKey((k) => k + 1); // garante que a lista recarregue ao voltar
  }

  function handleUploadDone(msg: string) {
    showToast(msg, msg.startsWith("Falha") ? "err" : "ok");
    if (!msg.startsWith("Falha")) {
      setRefreshKey((k) => k + 1); // força o FileList a recarregar
      setView("files"); // volta pra lista de arquivos
    }
  }

  function handleToggleAdmin() {
    setView((prev) => (prev === "admin" ? "files" : "admin"));
  }

  if (!sector) {
    return <SectorSelector onSectorSelected={handleSectorSelected} />;
  }

  return (
    <div className="app">
      <Header
        sector={sector}
        onChangeSector={handleBackToSectors}
        onUploadDone={handleUploadDone}
        onAdminClick={handleToggleAdmin}
        isAdmin={view === "admin"}
      />

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      {view === "admin" ? (
        <AdminPanel sector={sector} />
      ) : view === "files" ? (
        <FileList
          key={refreshKey}
          sector={sector}
          onFileSelected={handleFileSelected}
          onBack={handleBackToSectors}
        />
      ) : (
        <Chat
          sector={sector}
          source={selectedFile ?? undefined}
          topic={selectedTopic ?? undefined}
          onBackToFiles={selectedFile ? handleBackToFiles : undefined}
        />
      )}
    </div>
  );
}
