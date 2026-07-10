import { useState, useEffect } from "react";
import { listFiles, type FileInfo } from "../services/api";
import Spinner from "./Spinner";

interface FileListProps {
  sector: string;
  onFileSelected: (filename: string, topic?: string) => void;
  onBack: () => void;
}

const MAX_TOPICS = 6;
const MAX_SUBTOPICS = 4;

export default function FileList({ sector, onFileSelected, onBack }: FileListProps) {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedFile, setExpandedFile] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function fetch() {
      setLoading(true);
      setError(null);
      try {
        const data = await listFiles(sector);
        if (!cancelled) {
          setFiles(data);
          setExpandedFile(null);
        }
      } catch {
        if (!cancelled) setError("Erro ao carregar arquivos");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    fetch();
    return () => { cancelled = true; };
  }, [sector]);

  function fileInitials(name: string): string {
    const base = name.replace(/\.[^.]+$/, "");
    const parts = base.split(/[\s_-]+/);
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return name.substring(0, 2).toUpperCase();
  }

  return (
    <div className="file-list-container">
      <div className="file-list-header">
        <button className="file-back-btn" onClick={onBack}>←</button>
        <div className="file-list-header-info">
          <h2 className="file-list-title">{sector}</h2>
          <span className="file-list-subtitle">
            {loading ? "Carregando..." : `${files.length} arquivo(s)`}
          </span>
        </div>
      </div>

      {loading && <div className="file-list-loading"><Spinner text="Carregando arquivos..." /></div>}
      {error && !loading && <div className="file-list-error">{error}</div>}

      {!loading && !error && files.length === 0 && (
        <div className="file-list-empty">
          <p>Nenhum arquivo encontrado</p>
          <p className="file-list-empty-hint">
            Faça upload de documentos no setor "{sector}" para começar
          </p>
        </div>
      )}

      {!loading && !error && files.length > 0 && (
        <div className="file-list-scroll">
          {files.map((file) => {
            const isFileOpen = expandedFile === file.filename;
            return (
              <div key={file.filename} className="file-list-item">
                {/* ── NÍVEL 1: Arquivo ── */}
                <div className="file-item-main">
                  <button className="file-item-expand" onClick={() =>
                    setExpandedFile(isFileOpen ? null : file.filename)
                  }>
                    <span className={`file-item-chevron ${isFileOpen ? "file-item-chevron--open" : ""}`}>▶</span>
                  </button>
                  <button className="file-item-goto" onClick={() => onFileSelected(file.filename)}>
                    <span className="file-item-avatar">{fileInitials(file.filename)}</span>
                    <div className="file-item-info-text">
                      <span className="file-item-name">{file.filename}</span>
                      <span className="file-item-count">{file.topics.length} tópico(s)</span>
                    </div>
                  </button>
                </div>

                {/* ── NÍVEL 2: Tópicos ── */}
                {isFileOpen && file.topics.length > 0 && (
                  <div className="file-sublist">
                    <TopicList
                      topics={file.topics}
                      filename={file.filename}
                      onTopicClick={onFileSelected}
                    />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* ─── NÍVEL 2: Lista de tópicos ─────────────────────────────────────── */

function TopicList({
  topics,
  filename,
  onTopicClick,
}: {
  topics: FileInfo["topics"];
  filename: string;
  onTopicClick: (f: string, topic?: string) => void;
}) {
  const [showAll, setShowAll] = useState(false);
  const [expandedTopic, setExpandedTopic] = useState<string | null>(null);
  const visible = showAll ? topics : topics.slice(0, MAX_TOPICS);

  return (
    <div className="topic-list">
      {visible.map((t, i) => {
        const isTopicOpen = expandedTopic === t.topic;
        return (
          <div key={t.topic + i} className="topic-list-item">
            <div className="topic-list-row">
              <button
                className="topic-expand-btn"
                onClick={() => setExpandedTopic(isTopicOpen ? null : t.topic)}
                title="Ver subtópicos"
              >
                <span className={`topic-chevron ${isTopicOpen ? "topic-chevron--open" : ""}`}>▶</span>
              </button>
              <button
                className="topic-goto-btn"
                onClick={() => onTopicClick(filename, t.topic)}
                title="Ir para o chat"
              >
                <span className="topic-label">{t.topic}</span>
              </button>
            </div>

            {/* ── NÍVEL 3: Subtópicos ── */}
            {isTopicOpen && t.subtopics.length > 0 && (
              <SubTopicList subtopics={t.subtopics} />
            )}
          </div>
        );
      })}
      {topics.length > MAX_TOPICS && (
        <button className="topic-more-btn" onClick={() => setShowAll(!showAll)}>
          {showAll ? "⇡ Mostrar menos" : `⇣ Mais ${topics.length - MAX_TOPICS} tópicos`}
        </button>
      )}
    </div>
  );
}

/* ─── NÍVEL 3: Subtópicos (expansíveis → conteúdo completo) ───────────── */

function SubTopicList({
  subtopics,
}: {
  subtopics: FileInfo["topics"][number]["subtopics"];
}) {
  const [showAll, setShowAll] = useState(false);
  const [expandedSub, setExpandedSub] = useState<string | null>(null);
  const visible = showAll ? subtopics : subtopics.slice(0, MAX_SUBTOPICS);

  return (
    <div className="subtopic-list">
      {visible.map((s, i) => {
        const isOpen = expandedSub === s.subtopic;
        return (
          <div key={s.subtopic + i} className="subtopic-item">
            <div className="subtopic-row">
              <button
                className="subtopic-expand-btn"
                onClick={() => setExpandedSub(isOpen ? null : s.subtopic)}
                title="Ver conteúdo completo"
              >
                <span className={`subtopic-chevron ${isOpen ? "subtopic-chevron--open" : ""}`}>▶</span>
              </button>
              <span className="subtopic-label">{s.subtopic}</span>
            </div>

            {/* Conteúdo completo do subtópico, mostrado inline */}
            {isOpen && (
              <div className="subtopic-content">
                {s.content}
              </div>
            )}
          </div>
        );
      })}
      {subtopics.length > MAX_SUBTOPICS && (
        <button className="topic-more-btn" onClick={() => setShowAll(!showAll)}>
          {showAll ? "⇡ Menos" : `⇣ +${subtopics.length - MAX_SUBTOPICS}`}
        </button>
      )}
    </div>
  );
}
