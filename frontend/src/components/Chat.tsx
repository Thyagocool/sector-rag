import { useState, useRef, useEffect } from "react";
import { ask, askStream, type Source } from "../services/api";
import Spinner from "./Spinner";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

interface ChatProps {
  sector: string;
  source?: string;
  topic?: string;
  onBackToFiles?: () => void;
}

export default function Chat({ sector, source, topic, onBackToFiles }: ChatProps) {
  const initialMsg = topic
    ? `Faça uma pergunta sobre o tópico "${topic}" no arquivo "${source}".`
    : source
      ? `Faça uma pergunta sobre o arquivo "${source}".`
      : `Faça uma pergunta sobre os documentos do setor "${sector}".`;

  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: initialMsg },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showSources, setShowSources] = useState<number | null>(null);
  const chatRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    chatRef.current?.scrollTo({
      top: chatRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  // Reseta quando troca de setor, arquivo ou tópico
  useEffect(() => {
    const greeting = topic
      ? `Faça uma pergunta sobre o tópico "${topic}" no arquivo "${source}".`
      : source
        ? `Faça uma pergunta sobre o arquivo "${source}".`
        : `Faça uma pergunta sobre os documentos do setor "${sector}".`;
    setMessages([{ role: "assistant", content: greeting }]);
  }, [sector, source, topic]);

  async function handleSend() {
    const q = input.trim();
    if (!q || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setLoading(true);

    const assistantMsg: Message = { role: "assistant", content: "" };
    setMessages((prev) => [...prev, assistantMsg]);

    try {
      // Tenta streaming primeiro, fallback pra resposta completa
      let streamed = false;
      try {
        for await (const token of askStream(q, sector, source, topic)) {
          streamed = true;
          setMessages((prev) => {
            const idx = prev.length - 1;
            const last = prev[idx];
            if (last.role === "assistant") {
              const copy = [...prev];
              copy[idx] = { ...last, content: last.content + token };
              return copy;
            }
            return prev;
          });
        }
      } catch {
        // streaming falhou
      }

      if (!streamed) {
        const result = await ask(q, sector, source, topic);
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last.role === "assistant") {
            last.content = result.answer;
            last.sources = result.sources;
          }
          return [...updated];
        });
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Erro desconhecido";
      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last.role === "assistant") {
          last.content = `Erro: ${msg}`;
        }
        return [...updated];
      });
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function toggleSources(idx: number) {
    setShowSources(showSources === idx ? null : idx);
  }

  return (
    <div className="chat-container">
      {/* Context bar: mostra o arquivo selecionado */}
      {source && onBackToFiles && (
        <div className="chat-context-bar">
          <button className="chat-context-back" onClick={onBackToFiles}>
            ←
          </button>
          <div className="chat-context-info">
            <span className="chat-context-label">
              <strong>{source}</strong>
            </span>
            {topic && (
              <span className="chat-context-topic">
                {topic}
              </span>
            )}
          </div>
        </div>
      )}

      <div className="messages" ref={chatRef}>
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="avatar">
              {msg.role === "user" ? "U" : "AI"}
            </div>
            <div className="bubble">
              <div className="msg-content">
                  {msg.content || (loading && i === messages.length - 1 ? (
                    <Spinner size="md" />
                  ) : null)}
              </div>

              {msg.sources && msg.sources.length > 0 && (
                <div className="sources">
                  <button
                    className="sources-toggle"
                    onClick={() => toggleSources(i)}
                  >
                    Fontes ({msg.sources.length}) {showSources === i ? "▲" : "▼"}
                  </button>
                  {showSources === i && (
                    <div className="sources-list">
                      {msg.sources.map((s, j) => (
                        <div key={j} className="source-item">
                          <p className="source-text">{s.content}</p>
                          {s.metadata?.source != null && (
                            <span className="source-file">
                              {String(s.metadata.source)}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="input-area">
        <textarea
          ref={inputRef}
          className="input-box"
          placeholder={`Pergunte sobre os documentos do setor "${sector}"...`}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          disabled={loading}
        />
        <button
          className="btn btn-send"
          onClick={handleSend}
          disabled={loading || !input.trim()}
        >
          {loading ? "..." : "Enviar"}
        </button>
      </div>
    </div>
  );
}
