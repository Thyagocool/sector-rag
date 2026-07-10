import { useState, useEffect } from "react";

interface ToastProps {
  message: string;
  type: "ok" | "err";
  onClose: () => void;
  duration?: number;
}

export default function Toast({ message, type, onClose, duration = 4000 }: ToastProps) {
  const [exiting, setExiting] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setExiting(true);
      setTimeout(onClose, 300);
    }, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  return (
    <div className={`toast toast-${type} ${exiting ? "toast--exit" : "toast--enter"}`}>
      <span className="toast-icon">{type === "ok" ? "✓" : "✕"}</span>
      <span className="toast-message">{message}</span>
    </div>
  );
}
