import { Trophy } from "lucide-react";
import type { ScriptState } from "../types";

export function TabBar({
  scripts,
  active,
  onChange,
}: {
  scripts: ScriptState[];
  active: number;
  onChange: (index: number) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {scripts.map((script, index) => {
        const isActive = index === active;
        const complete = script.total > 0 && script.completed >= script.total;

        return (
          <button
            key={script.id}
            onClick={() => onChange(index)}
            className={`flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition ${
              isActive
                ? "bg-indigo-600 text-white shadow"
                : "border border-slate-200 bg-white text-slate-600 hover:border-indigo-300 hover:text-indigo-600"
            }`}
          >
            {complete && (
              <Trophy
                className={`h-4 w-4 ${isActive ? "text-amber-300" : "text-amber-500"}`}
              />
            )}
            <span>{script.title}</span>
            <span
              className={`rounded-md px-1.5 py-0.5 text-xs tabular-nums ${
                isActive ? "bg-white/20 text-white" : "bg-slate-100 text-slate-500"
              }`}
            >
              {script.completed}/{script.total}
            </span>
          </button>
        );
      })}
    </div>
  );
}
