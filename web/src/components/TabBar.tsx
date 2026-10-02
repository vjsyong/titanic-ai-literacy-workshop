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
            className={`flex h-9 items-center gap-2 border px-4 text-sm transition ${
              isActive
                ? "border-black bg-black font-semibold text-white"
                : "border-line bg-white font-medium text-[#3f3f46] hover:border-black hover:text-black"
            }`}
          >
            {complete && (
              <Trophy
                className={`h-4 w-4 ${isActive ? "text-warn" : "text-warn"}`}
              />
            )}
            <span>{script.title}</span>
            <span className="font-mono text-xs opacity-75">
              {script.completed}/{script.total}
            </span>
          </button>
        );
      })}
    </div>
  );
}
