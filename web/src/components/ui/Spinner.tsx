export default function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center justify-center gap-3 p-10 text-ink2">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-line border-t-accent" />
      {label && <span className="text-sm">{label}</span>}
    </div>
  );
}
