import { AlertTriangle } from "lucide-react";

export function ErrorBanner({
  errors,
}: {
  errors: Record<string, string | null>;
}) {
  const broken = Object.entries(errors).filter(
    (entry): entry is [string, string] => Boolean(entry[1]),
  );
  if (broken.length === 0) return null;

  return (
    <div className="rounded-2xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-800">
      <div className="flex items-center gap-2 font-semibold">
        <AlertTriangle className="h-4 w-4" />
        A workshop file has an error
      </div>
      {broken.map(([id, message]) => (
        <pre
          key={id}
          className="mt-2 max-h-36 overflow-auto whitespace-pre-wrap rounded-lg bg-white/70 p-2 font-mono text-xs"
        >
          {message.trim().split("\n").slice(-6).join("\n")}
        </pre>
      ))}
      <div className="mt-2 text-xs">
        The last good page is still shown. Ask your AI Teaching Assistant to
        fix the file, then save it again.
      </div>
    </div>
  );
}
