import { useState, useCallback } from "react";
import Header from "./components/Header";
import Chat from "./components/Chat";
import SectorSelector from "./components/SectorSelector";
import AdminPanel from "./components/AdminPanel";
import "./App.css";

export default function App() {
  const [sector, setSector] = useState<string | null>(null);
  const [view, setView] = useState<"chat" | "admin">("chat");
  const [notification, setNotification] = useState<string | null>(null);
  const [notifType, setNotifType] = useState<"ok" | "err">("ok");

  const showNotif = useCallback((msg: string, type: "ok" | "err" = "ok") => {
    setNotification(msg);
    setNotifType(type);
    setTimeout(() => setNotification(null), 4000);
  }, []);

  function handleSectorSelected(s: string) {
    setSector(s);
    showNotif(`Setor "${s}" selecionado`, "ok");
  }

  function handleUploadDone(msg: string) {
    showNotif(msg, msg.startsWith("Falha") ? "err" : "ok");
  }

  if (!sector) {
    return <SectorSelector onSectorSelected={handleSectorSelected} />;
  }

  return (
    <div className="app">
      <Header
        sector={sector}
        onChangeSector={() => setSector(null)}
        onUploadDone={handleUploadDone}
        onAdminClick={() => setView(view === "admin" ? "chat" : "admin")}
        isAdmin={view === "admin"}
      />

      {notification && (
        <div className={`notification ${notifType}`}>
          {notification}
        </div>
      )}

      {view === "admin" ? (
        <AdminPanel sector={sector} />
      ) : (
        <Chat sector={sector} />
      )}
    </div>
  );
}
