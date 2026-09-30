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
    <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/85 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center gap-4 px-4 py-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-sm">
          <Ship className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-base font-bold tracking-tight text-slate-800">
            Titanic AI Literacy Workshop
          </h1>
          <p className="hidden text-xs text-slate-500 sm:block">
            Explore · Train · Predict — one checkpoint at a time
          </p>
        </div>

        <div className="ml-auto flex items-center gap-4">
          <div className="hidden items-center gap-2 sm:flex">
            <div className="h-2 w-40 overflow-hidden rounded-full bg-slate-200">
              <div
                className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-teal-400 transition-all duration-700"
                style={{ width: `${percent}%` }}
              />
            </div>
            <span className="text-xs font-semibold tabular-nums text-slate-500">
              {done}/{total}
            </span>
          </div>
          <span
            className={`flex items-center gap-1.5 text-xs font-medium ${
              connected ? "text-emerald-600" : "text-amber-600"
            }`}
          >
            <span
              className={`h-2 w-2 rounded-full ${
                connected ? "bg-emerald-500" : "animate-pulse bg-amber-500"
              }`}
            />
            {connected ? "live" : "reconnecting…"}
          </span>
        </div>
      </div>
    </header>
  );
}
