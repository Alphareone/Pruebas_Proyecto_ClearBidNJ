import { type ReactNode } from "react";

export default function Chip({
  active,
  dot,
  onClick,
  children,
}: {
  active?: boolean;
  dot?: "g" | "a" | "r";
  onClick?: () => void;
  children: ReactNode;
}) {
  return (
    <span className={`chip ${active ? "chip-on" : ""}`} onClick={onClick}>
      {dot && <i className={`dot ${dot}`} />}
      {children}
    </span>
  );
}
