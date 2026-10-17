import { useToast } from "@/store/toast";

export default function Toast() {
  const message = useToast((s) => s.message);
  return (
    <div
      className={`fixed bottom-6 left-1/2 z-[100] -translate-x-1/2 rounded-[10px] bg-ink px-4 py-3 text-sm font-semibold text-paper shadow-lg transition-all duration-300 ${
        message ? "translate-y-0 opacity-100" : "pointer-events-none translate-y-3 opacity-0"
      }`}
    >
      {message}
    </div>
  );
}
