import { Ship } from "lucide-react";

export function Header({
  done,
  total,
  connected,
}: {
  done: number;
  total: number;
  connected: boolean;
}) {
  const percent = total > 0 ? Math.round((done / total) * 100) : 0;

  return (
    <header className="sticky top-0 z-30 border-b border-line bg-white">
      <div className="mx-auto flex max-w-6xl items-center gap-4 px-4 py-3">
        <div className="flex h-9 w-9 items-center justify-center bg-black text-white">
          <Ship className="h-4.5 w-4.5" />
        </div>
        <div>
          <h1 className="text-[0.98rem] font-bold tracking-tight text-ink">
            Titanic AI Literacy Workshop
          </h1>
          <p className="hidden text-xs text-dim sm:block">
            Explore · Train · Predict — one checkpoint at a time
          </p>
        </div>

        <div className="ml-auto flex items-center gap-4">
          <div className="hidden items-center gap-2 sm:flex">
            <div className="h-1.5 w-40 border border-line bg-card2">
              <div
                className="h-full bg-black transition-all duration-700"
                style={{ width: `${percent}%` }}
              />
            </div>
            <span className="font-mono text-xs text-dim">
              {done}/{total}
            </span>
          </div>
          <span
            className={`flex items-center gap-1.5 text-xs font-medium ${
              connected ? "text-ok" : "text-warn"
            }`}
          >
            <span
              className={`h-2 w-2 ${
                connected ? "bg-ok" : "animate-pulse bg-warn"
              }`}
            />
            {connected ? "live" : "reconnecting…"}
          </span>
        </div>
      </div>
    </header>
  );
}
