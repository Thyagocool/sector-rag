interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  text?: string;
}

export default function Spinner({ size = "md", text }: SpinnerProps) {
  return (
    <div className={`spinner spinner--${size}${text ? " spinner--with-text" : ""}`}>
      <div className="spinner-ring" />
      {text && <span className="spinner-text">{text}</span>}
    </div>
  );
}
